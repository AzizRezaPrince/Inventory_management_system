import os
import json
import time
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
    Hybrid NoSQL Database Manager.
    Uses Firebase Firestore if serviceAccountKey.json exists.
    Otherwise falls back to a local JSON NoSQL database engine for zero-install local operation.
    """
    def __init__(self):
        self.use_firebase = False
        self.db = None
        self.local_db_path = os.path.join(os.path.dirname(__file__), 'data', 'db.json')
        
        # Check for Firebase Service Account Key
        key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        if FIREBASE_AVAILABLE and os.path.exists(key_path):
            try:
                cred = credentials.Certificate(key_path)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.use_firebase = True
                print("Connected to Firebase Firestore!")
            except Exception as e:
                print(f"Firebase initialization warning: {e}. Falling back to Local NoSQL engine.")
                self.use_firebase = False
        else:
            print("Running in Local NoSQL Mode (Zero-Install).")
        
        if not self.use_firebase:
            self._ensure_local_db()

    def _ensure_local_db(self):
        os.makedirs(os.path.dirname(self.local_db_path), exist_ok=True)
        if not os.path.exists(self.local_db_path):
            initial_data = {
                "settings": {
                    "id": "global_settings",
                    "shop_name": "ElectroIMS",
                    "shop_tagline": "Electronics Shop & Repair Hub",
                    "shop_phone": "9849284991",
                    "shop_address": "Kathmandu, Nepal"
                },
                "users": [
                    {
                        "id": "54",
                        "fullname": "Shawon Sarwar",
                        "location": "Pokhara",
                        "phone": "9849284991",
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
                "repairs": []
            }
            with open(self.local_db_path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=4)

    def _read_local(self):
        self._ensure_local_db()
        with open(self.local_db_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write_local(self, data):
        with open(self.local_db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    # --- Settings Operations ---

    def get_settings(self):
        default_settings = {
            "id": "global_settings",
            "shop_name": "ElectroIMS",
            "shop_tagline": "Electronics Shop & Repair Hub",
            "shop_phone": "9849284991",
            "shop_address": "Kathmandu, Nepal"
        }
        if self.use_firebase:
            doc = self.db.collection('settings').document('global_settings').get()
            if doc.exists:
                res = doc.to_dict()
                default_settings.update(res)
                return default_settings
            else:
                self.db.collection('settings').document('global_settings').set(default_settings)
                return default_settings
        else:
            data = self._read_local()
            if 'settings' not in data:
                data['settings'] = default_settings
                self._write_local(data)
            return data.get('settings', default_settings)

    def update_settings(self, updates):
        if self.use_firebase:
            self.db.collection('settings').document('global_settings').set(updates, merge=True)
        else:
            data = self._read_local()
            if 'settings' not in data:
                data['settings'] = {}
            data['settings'].update(updates)
            self._write_local(data)

    # --- Collection Generic Operations ---

    def get_collection(self, collection_name):
        if self.use_firebase:
            docs = self.db.collection(collection_name).stream()
            result = []
            for doc in docs:
                item = doc.to_dict()
                item['id'] = doc.id
                result.append(item)
            return result
        else:
            data = self._read_local()
            return data.get(collection_name, [])

    def get_doc(self, collection_name, doc_id):
        if self.use_firebase:
            doc = self.db.collection(collection_name).document(str(doc_id)).get()
            if doc.exists:
                res = doc.to_dict()
                res['id'] = doc.id
                return res
            return None
        else:
            data = self._read_local()
            items = data.get(collection_name, [])
            for item in items:
                if str(item.get('id')) == str(doc_id):
                    return item
            return None

    def add_doc(self, collection_name, item):
        if self.use_firebase:
            if 'id' in item and item['id']:
                doc_ref = self.db.collection(collection_name).document(str(item['id']))
                doc_ref.set(item)
                return str(item['id'])
            else:
                _, doc_ref = self.db.collection(collection_name).add(item)
                return doc_ref.id
        else:
            data = self._read_local()
            if collection_name not in data:
                data[collection_name] = []
            
            if 'id' not in item or not item['id']:
                item['id'] = str(int(time.time() * 1000))
            
            data[collection_name].append(item)
            self._write_local(data)
            return item['id']

    def update_doc(self, collection_name, doc_id, updates):
        if self.use_firebase:
            self.db.collection(collection_name).document(str(doc_id)).update(updates)
        else:
            data = self._read_local()
            items = data.get(collection_name, [])
            for i, item in enumerate(items):
                if str(item.get('id')) == str(doc_id):
                    items[i].update(updates)
                    break
            data[collection_name] = items
            self._write_local(data)

    def delete_doc(self, collection_name, doc_id):
        if self.use_firebase:
            self.db.collection(collection_name).document(str(doc_id)).delete()
        else:
            data = self._read_local()
            items = data.get(collection_name, [])
            data[collection_name] = [item for item in items if str(item.get('id')) != str(doc_id)]
            self._write_local(data)

    # --- Domain Specific Auto-Sync Helpers ---

    def ensure_customer_exists(self, customer_name, phone=""):
        if not customer_name or customer_name.strip().lower() == "walk-in customer":
            return
        cname = customer_name.strip()
        customers = self.get_collection('customers')
        for c in customers:
            if c.get('fullname', '').strip().lower() == cname.lower():
                return
        
        # Create new customer record dynamically
        ccode = f"cus{int(time.time()) % 1000}"
        self.add_doc('customers', {
            'customercode': ccode,
            'fullname': cname,
            'location': 'Local Counter',
            'phone': phone or 'N/A'
        })

    def ensure_supplier_exists(self, supplier_name):
        if not supplier_name or supplier_name.strip().lower() == "general supplier":
            return
        sname = supplier_name.strip()
        suppliers = self.get_collection('suppliers')
        for s in suppliers:
            if s.get('fullname', '').strip().lower() == sname.lower():
                return
        
        # Create new supplier record dynamically
        scode = f"sup{int(time.time()) % 1000}"
        self.add_doc('suppliers', {
            'suppliercode': scode,
            'fullname': sname,
            'location': 'Local Market',
            'phone': 'N/A'
        })

    def authenticate_user(self, username, password):
        users = self.get_collection('users')
        for user in users:
            if user.get('username') == username and user.get('password') == password:
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
