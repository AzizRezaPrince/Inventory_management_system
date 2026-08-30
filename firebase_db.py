import os
import json
import time
import base64
from datetime import datetime

# Optional Firebase import
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

class DatabaseManager:
    """
    Hybrid Cloud NoSQL Database Manager with Auto-Sync & Dual Persistence.
    Uses Firebase Firestore as primary cloud database (when configured or credential file exists).
    Maintains a synchronized local NoSQL database (data/db.json) as backup/cache.
    Ensures 100% data persistence on localhost and live deployments (Render, Vercel, Railway, PythonAnywhere, etc.).
    """
    def __init__(self):
        self.use_firebase = False
        self.db = None
        self.project_id = "Local NoSQL"
        self.local_db_path = os.path.join(os.path.dirname(__file__), 'data', 'db.json')
        
        # Ensure local db directory & default file exist
        self._ensure_local_db()

        # Initialize Firebase Connection
        if FIREBASE_AVAILABLE:
            self._init_firebase()

        # Auto Seed & Sync between Local DB and Firebase Firestore on startup
        if self.use_firebase:
            try:
                self._auto_seed_and_sync()
            except Exception as ex:
                print(f"Warning during Firebase initial sync: {ex}")

    def _init_firebase(self):
        cred = None
        
        # 1. Check Environment Variables (useful for cloud deployments like Render/Heroku/Vercel/Railway)
        env_cred_sources = [
            os.environ.get('FIREBASE_CREDENTIALS'),
            os.environ.get('FIREBASE_SERVICE_ACCOUNT'),
            os.environ.get('FIREBASE_KEY')
        ]
        
        for env_val in env_cred_sources:
            if not env_val:
                continue
            env_val = env_val.strip()
            
            # Try raw JSON or Base64 decoded JSON
            cred_dict = None
            try:
                if env_val.startswith('{'):
                    cred_dict = json.loads(env_val)
                elif os.path.exists(env_val):
                    with open(env_val, 'r', encoding='utf-8') as f:
                        cred_dict = json.load(f)
                else:
                    # Attempt base64 decoding
                    decoded = base64.b64decode(env_val).decode('utf-8')
                    cred_dict = json.loads(decoded)
            except Exception as ex:
                print(f"Error parsing environment credentials: {ex}")
                cred_dict = None

            if cred_dict and isinstance(cred_dict, dict):
                # Fix escaped newlines in private key if string escaped
                if 'private_key' in cred_dict and isinstance(cred_dict['private_key'], str):
                    cred_dict['private_key'] = cred_dict['private_key'].replace('\\n', '\n')
                try:
                    cred = credentials.Certificate(cred_dict)
                    print("Loaded Firebase credentials from Environment Variable.")
                    break
                except Exception as ex:
                    print(f"Failed to create Certificate from env dict: {ex}")

        # 2. Check local key files in project root directory
        if not cred:
            base_dir = os.path.dirname(__file__)
            possible_keys = ['serviceAccountKey.json']
            try:
                possible_keys += [f for f in os.listdir(base_dir) if f.endswith('.json') and 'firebase-adminsdk' in f]
            except Exception:
                pass

            for k_name in set(possible_keys):
                k_path = os.path.join(base_dir, k_name)
                if os.path.exists(k_path):
                    try:
                        cred = credentials.Certificate(k_path)
                        print(f"Loaded Firebase key file: {k_name}")
                        break
                    except Exception as ex:
                        print(f"Failed to load key file {k_name}: {ex}")

        if cred:
            try:
                if not firebase_admin._apps:
                    firebase_admin.initialize_app(cred)
                client = firestore.client()
                
                # Perform healthcheck query
                _ = client.collection('_healthcheck').document('test').get()
                self.db = client
                self.use_firebase = True
                
                # Extract project ID if possible
                try:
                    if hasattr(cred, 'project_id') and cred.project_id:
                        self.project_id = cred.project_id
                    else:
                        self.project_id = self.db.project
                except Exception:
                    self.project_id = "inventorymanagementsyste-e864a"

                print(f"Successfully connected to Firebase Firestore Cloud DB [{self.project_id}]!")
            except Exception as e:
                print(f"Firebase connection warning: {e}. Falling back to Local NoSQL Mode.")
                self.use_firebase = False
        else:
            print("Running in Local NoSQL Mode (Zero-Install / Offline).")

    def _ensure_local_db(self):
        os.makedirs(os.path.dirname(self.local_db_path), exist_ok=True)
        if not os.path.exists(self.local_db_path):
            initial_data = {
                "settings": {
                    "id": "global_settings",
                    "shop_name": "SS Technology",
                    "shop_tagline": "Electronics Shop & Repair Hub",
                    "shop_phone": "01700000000",
                    "shop_address": "Club Super Market 2nd Floor, Chapainawabganj"
                },
                "users": [
                    {
                        "id": "1",
                        "fullname": "Abdul Wadud",
                        "location": "Chapainawabganj",
                        "phone": "01700000000",
                        "username": "admin",
                        "password": "admin",
                        "category": "ADMINISTRATOR"
                    },
                    {
                        "id": "54",
                        "fullname": "Abdul Wadud",
                        "location": "Dhaka",
                        "phone": "01700000000",
                        "username": "user4",
                        "password": "user4",
                        "category": "ADMINISTRATOR"
                    }
                ],
                "products": [],
                "currentstocks": [],
                "suppliers": [],
                "customers": [],
                "purchaseinfo": [],
                "salesreport": [],
                "repairs": [],
                "expenses": [],
                "activity_logs": []
            }
            with open(self.local_db_path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=4)

    def _read_local(self):
        self._ensure_local_db()
        try:
            with open(self.local_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_local(self, data):
        try:
            with open(self.local_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as ex:
            print(f"Error updating local db cache: {ex}")

    def _auto_seed_and_sync(self):
        """
        Auto Seeds empty Firebase Firestore collections with local data.
        Syncs existing Firebase Firestore documents back to local db.json cache.
        """
        if not self.use_firebase:
            return

        local_data = self._read_local()
        collections_to_sync = [
            'settings', 'users', 'products', 'currentstocks', 
            'suppliers', 'customers', 'purchaseinfo', 'salesreport', 
            'repairs', 'expenses', 'activity_logs'
        ]

        for col in collections_to_sync:
            try:
                if col == 'settings':
                    doc = self.db.collection('settings').document('global_settings').get()
                    if not doc.exists:
                        s_data = local_data.get('settings', {
                            "id": "global_settings",
                            "shop_name": "SS Technology",
                            "shop_tagline": "Electronics Shop & Repair Hub",
                            "shop_phone": "01700000000",
                            "shop_address": "Club Super Market 2nd Floor, Chapainawabganj"
                        })
                        self.db.collection('settings').document('global_settings').set(s_data)
                    else:
                        local_data['settings'] = doc.to_dict()
                else:
                    fb_docs = list(self.db.collection(col).stream())
                    if not fb_docs and local_data.get(col):
                        print(f"Seeding empty Firebase collection '{col}' with {len(local_data[col])} local items...")
                        for item in local_data[col]:
                            doc_id = str(item.get('id', int(time.time() * 1000)))
                            item['id'] = doc_id
                            self.db.collection(col).document(doc_id).set(item)
                    elif fb_docs:
                        synced_items = []
                        for d in fb_docs:
                            d_dict = d.to_dict()
                            d_dict['id'] = d.id
                            synced_items.append(d_dict)
                        local_data[col] = synced_items
            except Exception as ex:
                print(f"Auto-sync exception for collection '{col}': {ex}")

        self._write_local(local_data)

    def sync_all_to_firebase(self):
        """
        Forces a full push of all local JSON data into Firebase Firestore.
        Useful for manual synchronization from Settings panel.
        """
        if not self.use_firebase:
            return False, "Firebase is not connected."

        local_data = self._read_local()
        count = 0
        try:
            # Sync Settings
            if 'settings' in local_data:
                self.db.collection('settings').document('global_settings').set(local_data['settings'], merge=True)
                count += 1

            collections = ['users', 'products', 'currentstocks', 'suppliers', 'customers', 'purchaseinfo', 'salesreport', 'repairs', 'expenses', 'activity_logs']
            for col in collections:
                items = local_data.get(col, [])
                for item in items:
                    doc_id = str(item.get('id', int(time.time() * 1000)))
                    item['id'] = doc_id
                    self.db.collection(col).document(doc_id).set(item, merge=True)
                    count += 1
            return True, f"Successfully synced {count} records/documents to Firebase Firestore Cloud DB!"
        except Exception as ex:
            return False, f"Failed to sync to Firebase: {ex}"

    # --- Settings Operations ---

    def get_settings(self):
        default_settings = {
            "id": "global_settings",
            "shop_name": "SS Technology",
            "shop_tagline": "Electronics Shop & Repair Hub",
            "shop_phone": "01700000000",
            "shop_address": "Club Super Market 2nd Floor, Chapainawabganj"
        }
        if self.use_firebase:
            try:
                doc = self.db.collection('settings').document('global_settings').get()
                if doc.exists:
                    res = doc.to_dict()
                    default_settings.update(res)
                    
                    # Backup to local DB cache
                    local_data = self._read_local()
                    local_data['settings'] = default_settings
                    self._write_local(local_data)

                    return default_settings
                else:
                    self.db.collection('settings').document('global_settings').set(default_settings)
                    return default_settings
            except Exception as e:
                print(f"Firestore get_settings error: {e}. Falling back to local cache.")
        
        data = self._read_local()
        if 'settings' not in data:
            data['settings'] = default_settings
            self._write_local(data)
        return data.get('settings', default_settings)

    def update_settings(self, updates):
        # Update local cache first
        data = self._read_local()
        if 'settings' not in data:
            data['settings'] = {}
        data['settings'].update(updates)
        self._write_local(data)

        # Sync to Firebase Firestore
        if self.use_firebase:
            try:
                self.db.collection('settings').document('global_settings').set(updates, merge=True)
            except Exception as ex:
                print(f"Firestore update_settings error: {ex}")

    # --- Collection Generic Operations ---

    def get_collection(self, collection_name):
        if self.use_firebase:
            try:
                docs = self.db.collection(collection_name).stream()
                result = []
                for doc in docs:
                    item = doc.to_dict()
                    item['id'] = doc.id
                    result.append(item)
                
                # Update local cache backup
                local_data = self._read_local()
                local_data[collection_name] = result
                self._write_local(local_data)
                
                return result
            except Exception as ex:
                print(f"Firestore get_collection error for '{collection_name}': {ex}. Returning local cache.")

        data = self._read_local()
        return data.get(collection_name, [])

    def get_doc(self, collection_name, doc_id):
        if self.use_firebase:
            try:
                doc = self.db.collection(collection_name).document(str(doc_id)).get()
                if doc.exists:
                    res = doc.to_dict()
                    res['id'] = doc.id
                    return res
            except Exception as ex:
                print(f"Firestore get_doc error: {ex}")
        
        data = self._read_local()
        items = data.get(collection_name, [])
        for item in items:
            if str(item.get('id')) == str(doc_id):
                return item
        return None

    def add_doc(self, collection_name, item):
        if 'id' not in item or not item['id']:
            item['id'] = str(int(time.time() * 1000))
        doc_id = str(item['id'])

        # 1. Update local cache
        data = self._read_local()
        if collection_name not in data:
            data[collection_name] = []
        
        # Replace if exists, else append
        existing_idx = next((i for i, x in enumerate(data[collection_name]) if str(x.get('id')) == doc_id), None)
        if existing_idx is not None:
            data[collection_name][existing_idx] = item
        else:
            data[collection_name].append(item)
        self._write_local(data)

        # 2. Write to Firebase Firestore
        if self.use_firebase:
            try:
                self.db.collection(collection_name).document(doc_id).set(item, merge=True)
            except Exception as ex:
                print(f"Firestore add_doc error for '{collection_name}': {ex}")

        return doc_id

    def update_doc(self, collection_name, doc_id, updates):
        doc_id = str(doc_id)
        
        # 1. Update local cache
        data = self._read_local()
        items = data.get(collection_name, [])
        for i, item in enumerate(items):
            if str(item.get('id')) == doc_id:
                items[i].update(updates)
                break
        data[collection_name] = items
        self._write_local(data)

        # 2. Update Firebase Firestore
        if self.use_firebase:
            try:
                self.db.collection(collection_name).document(doc_id).set(updates, merge=True)
            except Exception as ex:
                print(f"Firestore update_doc error for '{collection_name}': {ex}")

    def delete_doc(self, collection_name, doc_id):
        doc_id = str(doc_id)

        # 1. Update local cache
        data = self._read_local()
        items = data.get(collection_name, [])
        data[collection_name] = [item for item in items if str(item.get('id')) != doc_id]
        self._write_local(data)

        # 2. Update Firebase Firestore
        if self.use_firebase:
            try:
                self.db.collection(collection_name).document(doc_id).delete()
            except Exception as ex:
                print(f"Firestore delete_doc error for '{collection_name}': {ex}")

    # --- Domain Specific Auto-Sync Helpers ---

    def ensure_customer_exists(self, customer_name, phone=""):
        if not customer_name or customer_name.strip().lower() == "walk-in customer":
            return
        cname = customer_name.strip()
        customers = self.get_collection('customers')
        for c in customers:
            if c.get('fullname', '').strip().lower() == cname.lower():
                return
        
        ccode = f"cus{int(time.time()) % 1000}"
        self.add_doc('customers', {
            'customercode': ccode,
            'fullname': cname,
            'location': 'Dhaka',
            'phone': phone or 'N/A'
        })

    def ensure_supplier_exists(self, supplier_name, phone="N/A", location="Dhaka"):
        if not supplier_name or supplier_name.strip().lower() == "general supplier":
            return
        sname = supplier_name.strip()
        suppliers = self.get_collection('suppliers')
        for s in suppliers:
            if s.get('fullname', '').strip().lower() == sname.lower():
                if phone and phone != "N/A" and (s.get('phone') == "N/A" or not s.get('phone')):
                    self.update_doc('suppliers', s.get('id'), {'phone': phone, 'location': location or 'Dhaka'})
                return
        
        existing_codes = [s.get('suppliercode', '') for s in suppliers]
        max_num = 1000
        for code in existing_codes:
            if str(code).startswith('SUP-'):
                try:
                    num = int(str(code).split('SUP-')[1])
                    if num > max_num: max_num = num
                except ValueError:
                    pass
        scode = f"SUP-{max_num + 1}"

        self.add_doc('suppliers', {
            'suppliercode': scode,
            'fullname': sname,
            'location': location or 'Dhaka',
            'phone': phone or 'N/A'
        })

    def authenticate_user(self, username, password):
        users = self.get_collection('users')
        if not users:
            # Fallback Admin account if users collection is empty
            default_admin = {
                "id": "1",
                "fullname": "Abdul Wadud",
                "location": "Chapainawabganj",
                "phone": "01700000000",
                "username": "admin",
                "password": "admin",
                "category": "ADMINISTRATOR"
            }
            self.add_doc('users', default_admin)
            users = [default_admin]

        for user in users:
            if str(user.get('username')).strip() == username and str(user.get('password')).strip() == password:
                return user
        return None

    def get_stock(self, productcode):
        stocks = self.get_collection('currentstocks')
        for s in stocks:
            if s.get('productcode') == productcode:
                return int(s.get('quantity', 0))
        return 0

    def update_stock(self, productcode, delta_quantity):
        stocks = self.get_collection('currentstocks')
        found = False
        for s in stocks:
            if s.get('productcode') == productcode:
                new_qty = max(0, int(s.get('quantity', 0)) + delta_quantity)
                self.update_doc('currentstocks', s['id'], {'quantity': new_qty})
                found = True
                break
        if not found:
            self.add_doc('currentstocks', {
                'productcode': productcode,
                'quantity': max(0, delta_quantity)
            })

db = DatabaseManager()
