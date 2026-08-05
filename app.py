import os
import shutil
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from firebase_db import db

# --- Legacy Java/MySQL Cleanup Routine ---
for _legacy_file in ["InventoryMangagementSystem.jar", "README.TXT", "ims.sql", "run.bat", "cleanup_legacy.py"]:
    _p = os.path.join(os.path.dirname(__file__), _legacy_file)
    if os.path.exists(_p):
        try:
            os.remove(_p)
            print(f"Cleaned up legacy file: {_legacy_file}")
        except Exception:
            pass

_legacy_lib = os.path.join(os.path.dirname(__file__), "lib")
if os.path.exists(_legacy_lib):
    try:
        shutil.rmtree(_legacy_lib)
        print("Cleaned up legacy lib folder.")
    except Exception:
        pass

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'electronics_shop_ims_secret_2026')

# --- Context Processor for Global Shop Settings ---
@app.context_processor
def inject_global_settings():
    settings = db.get_settings()
    return dict(shop_settings=settings)

# --- Authentication Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access the system.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('category') != 'ADMINISTRATOR':
            flash('Admin access required for this action.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = db.authenticate_user(username, password)
        if user:
            session['user_id'] = user.get('id')
            session['username'] = user.get('username')
            session['fullname'] = user.get('fullname')
            session['category'] = user.get('category')
            flash(f"Welcome back, {user.get('fullname')}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    products = db.get_collection('products')
    repairs = db.get_collection('repairs')
    suppliers = db.get_collection('suppliers')
    sales = db.get_collection('salesreport')
    stocks = db.get_collection('currentstocks')

    # Build Stock Map
    stock_map = {s.get('productcode'): int(s.get('quantity', 0)) for s in stocks}

    total_products = len(products)
    total_stock_count = sum(stock_map.values())
    total_suppliers = len(suppliers)
    
    # Revenue Calculation
    total_revenue = sum(float(s.get('revenue', 0)) for s in sales)
    
    # Repairs Metrics
    active_repairs = [r for r in repairs if r.get('status') not in ['Delivered', 'Cancelled']]
    pending_repair_count = len(active_repairs)
    
    # Low Stock Items (< 5 quantity)
    low_stock_list = []
    for p in products:
        pcode = p.get('productcode')
        qty = stock_map.get(pcode, 0)
        if qty < 5:
            low_stock_list.append({
                'code': pcode,
                'name': p.get('productname'),
                'brand': p.get('brand'),
                'quantity': qty
            })

    return render_template(
        'dashboard.html',
        total_products=total_products,
        total_stock_count=total_stock_count,
        total_suppliers=total_suppliers,
        total_revenue=total_revenue,
        pending_repair_count=pending_repair_count,
        active_repairs=active_repairs[:5],
        low_stock_list=low_stock_list
    )

# --- Settings & Profile Management ---

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user_id = session.get('user_id')
    current_user = db.get_doc('users', user_id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_shop_settings':
            if session.get('category') != 'ADMINISTRATOR':
                flash('Only Administrators can change Shop Branding & Settings.', 'danger')
                return redirect(url_for('settings'))

            shop_name = request.form.get('shop_name', '').strip()
            shop_tagline = request.form.get('shop_tagline', '').strip()
            shop_phone = request.form.get('shop_phone', '').strip()
            shop_address = request.form.get('shop_address', '').strip()

            db.update_settings({
                'shop_name': shop_name or 'ElectroIMS',
                'shop_tagline': shop_tagline or 'Shop & Repair Hub',
                'shop_phone': shop_phone,
                'shop_address': shop_address
            })
            flash('Shop branding and project settings updated successfully!', 'success')

        elif action == 'update_profile':
            fullname = request.form.get('fullname', '').strip()
            username = request.form.get('username', '').strip()
            new_password = request.form.get('password', '').strip()
            location = request.form.get('location', '').strip()
            phone = request.form.get('phone', '').strip()

            updates = {
                'fullname': fullname,
                'username': username,
                'location': location,
                'phone': phone
            }
            if new_password:
                updates['password'] = new_password

            db.update_doc('users', user_id, updates)

            # Update active session credentials
            session['fullname'] = fullname
            session['username'] = username
            flash('Your profile and login information have been updated!', 'success')

        return redirect(url_for('settings'))

    current_settings = db.get_settings()
    return render_template('settings.html', settings=current_settings, user=current_user)

# --- Product Inventory Management ---

@app.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            pcode = request.form.get('productcode', '').strip()
            pname = request.form.get('productname', '').strip()
            brand = request.form.get('brand', '').strip() or 'General'
            cost = float(request.form.get('costprice', 0))
            sell = float(request.form.get('sellingprice', 0))
            init_qty = int(request.form.get('initial_quantity', 0))

            if not pcode:
                pcode = f"prod{int(datetime.now().timestamp()) % 1000}"

            doc_id = db.add_doc('products', {
                'productcode': pcode,
                'productname': pname,
                'brand': brand,
                'costprice': cost,
                'sellingprice': sell
            })
            db.update_stock(pcode, init_qty)
            flash(f'Product "{pname}" added with {init_qty} stock units!', 'success')

        elif action == 'edit':
            pid = request.form.get('pid')
            pcode = request.form.get('productcode', '').strip()
            pname = request.form.get('productname', '').strip()
            brand = request.form.get('brand', '').strip()
            cost = float(request.form.get('costprice', 0))
            sell = float(request.form.get('sellingprice', 0))

            db.update_doc('products', pid, {
                'productcode': pcode,
                'productname': pname,
                'brand': brand,
                'costprice': cost,
                'sellingprice': sell
            })
            flash('Product details updated.', 'success')

        elif action == 'delete':
            pid = request.form.get('pid')
            db.delete_doc('products', pid)
            flash('Product deleted from database.', 'info')

        return redirect(url_for('products'))

    products_list = db.get_collection('products')
    stocks = db.get_collection('currentstocks')
    stock_map = {s.get('productcode'): int(s.get('quantity', 0)) for s in stocks}

    for p in products_list:
        p['quantity'] = stock_map.get(p.get('productcode'), 0)

    return render_template('products.html', products=products_list)

# --- Electronics Repair & Service Management ---

@app.route('/repairs', methods=['GET', 'POST'])
@login_required
def repairs():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            ticket_id = f"RPR-{int(datetime.now().timestamp()) % 10000:04d}"
            cname = request.form.get('customer_name', '').strip() or 'Walk-in Customer'
            cphone = request.form.get('customer_phone', '').strip()
            dtype = request.form.get('device_type', '').strip() or 'Electronics Item'
            brand_model = request.form.get('brand_model', '').strip()
            sn = request.form.get('serial_number', '').strip()
            issue = request.form.get('issue_description', '').strip()
            est_cost = float(request.form.get('estimated_cost', 0))
            adv_paid = float(request.form.get('advance_paid', 0))
            tech = request.form.get('technician', '').strip()
            est_delivery = request.form.get('estimated_delivery', '')

            # Auto-sync Customer to Database
            db.ensure_customer_exists(cname, cphone)

            repair_item = {
                'id': ticket_id,
                'customer_name': cname,
                'customer_phone': cphone,
                'device_type': dtype,
                'brand_model': brand_model,
                'serial_number': sn,
                'issue_description': issue,
                'estimated_cost': est_cost,
                'advance_paid': adv_paid,
                'technician': tech or session.get('fullname', 'Staff'),
                'status': 'Received',
                'estimated_delivery': est_delivery,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            db.add_doc('repairs', repair_item)
            flash(f'Repair Ticket #{ticket_id} created & customer synced!', 'success')

        elif action == 'update_status':
            ticket_id = request.form.get('ticket_id')
            new_status = request.form.get('status')
            add_cost = float(request.form.get('additional_cost', 0))
            add_paid = float(request.form.get('additional_paid', 0))
            
            repair_doc = db.get_doc('repairs', ticket_id)
            if repair_doc:
                curr_cost = float(repair_doc.get('estimated_cost', 0)) + add_cost
                curr_paid = float(repair_doc.get('advance_paid', 0)) + add_paid
                db.update_doc('repairs', ticket_id, {
                    'status': new_status,
                    'estimated_cost': curr_cost,
                    'advance_paid': curr_paid
                })
                flash(f'Ticket #{ticket_id} status updated to "{new_status}".', 'success')

        elif action == 'delete':
            ticket_id = request.form.get('ticket_id')
            db.delete_doc('repairs', ticket_id)
            flash(f'Repair Ticket #{ticket_id} removed.', 'info')

        return redirect(url_for('repairs'))

    repairs_list = db.get_collection('repairs')
    repairs_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return render_template('repairs.html', repairs=repairs_list)

# --- Suppliers Management ---

@app.route('/suppliers', methods=['GET', 'POST'])
@login_required
def suppliers():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            scode = request.form.get('suppliercode', '').strip()
            fname = request.form.get('fullname', '').strip()
            location = request.form.get('location', '').strip()
            phone = request.form.get('phone', '').strip()

            if not scode:
                scode = f"sup{int(datetime.now().timestamp()) % 1000}"

            db.add_doc('suppliers', {
                'suppliercode': scode,
                'fullname': fname,
                'location': location,
                'phone': phone
            })
            flash(f'Supplier "{fname}" added to database.', 'success')

        elif action == 'delete':
            sid = request.form.get('sid')
            db.delete_doc('suppliers', sid)
            flash('Supplier deleted.', 'info')

        return redirect(url_for('suppliers'))

    suppliers_list = db.get_collection('suppliers')
    return render_template('suppliers.html', suppliers=suppliers_list)

# --- Customers Management ---

@app.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            ccode = request.form.get('customercode', '').strip()
            fname = request.form.get('fullname', '').strip()
            location = request.form.get('location', '').strip()
            phone = request.form.get('phone', '').strip()

            if not ccode:
                ccode = f"cus{int(datetime.now().timestamp()) % 1000}"

            db.add_doc('customers', {
                'customercode': ccode,
                'fullname': fname,
                'location': location,
                'phone': phone
            })
            flash(f'Customer "{fname}" saved.', 'success')

        elif action == 'delete':
            cid = request.form.get('cid')
            db.delete_doc('customers', cid)
            flash('Customer deleted.', 'info')

        return redirect(url_for('customers'))

    customers_list = db.get_collection('customers')
    return render_template('customers.html', customers=customers_list)

# --- Purchases Logging ---

@app.route('/purchases', methods=['GET', 'POST'])
@login_required
def purchases():
    if request.method == 'POST':
        sinput = request.form.get('supplier_input', '').strip() or request.form.get('suppliercode', '').strip() or 'General Supplier'
        pcode = request.form.get('productcode')
        qty = int(request.form.get('quantity', 0))
        total_cost = float(request.form.get('totalcost', 0))

        # Auto-sync Supplier into DB if new!
        db.ensure_supplier_exists(sinput)

        purchase_doc = {
            'suppliercode': sinput,
            'productcode': pcode,
            'quantity': qty,
            'totalcost': total_cost,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        db.add_doc('purchaseinfo', purchase_doc)
        db.update_stock(pcode, qty)
        flash(f'Stock purchase of {qty} unit(s) logged & inventory updated!', 'success')
        return redirect(url_for('purchases'))

    purchases_list = db.get_collection('purchaseinfo')
    suppliers_list = db.get_collection('suppliers')
    products_list = db.get_collection('products')
    return render_template('purchases.html', purchases=purchases_list, suppliers=suppliers_list, products=products_list)

# --- Sales Logging & Reports ---

@app.route('/sales', methods=['GET', 'POST'])
@login_required
def sales():
    if request.method == 'POST':
        pcode = request.form.get('productcode')
        cinput = request.form.get('customer_input', '').strip() or request.form.get('customercode', '').strip() or 'Walk-in Customer'
        qty = int(request.form.get('quantity', 0))
        
        curr_stock = db.get_stock(pcode)
        if qty > curr_stock:
            flash(f'Insufficient stock! Available: {curr_stock}, Requested: {qty}', 'danger')
            return redirect(url_for('sales'))

        # Auto-sync Customer into DB if new!
        db.ensure_customer_exists(cinput)

        # Calculate revenue based on selling price
        products = db.get_collection('products')
        selling_price = 0
        for p in products:
            if p.get('productcode') == pcode:
                selling_price = float(p.get('sellingprice', 0))
                break

        revenue = selling_price * qty
        sale_doc = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'productcode': pcode,
            'customercode': cinput,
            'quantity': qty,
            'revenue': revenue,
            'soldby': session.get('username', 'user')
        }
        db.add_doc('salesreport', sale_doc)
        db.update_stock(pcode, -qty)
        flash(f'Sale of {qty} unit(s) processed & stock updated in DB!', 'success')
        return redirect(url_for('sales'))

    sales_list = db.get_collection('salesreport')
    products_list = db.get_collection('products')
    customers_list = db.get_collection('customers')
    return render_template('sales.html', sales=sales_list, products=products_list, customers=customers_list)

# --- User Management (Admin Only) ---

@app.route('/users', methods=['GET', 'POST'])
@admin_required
def users():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            fullname = request.form.get('fullname', '').strip()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            category = request.form.get('category', 'USER')
            location = request.form.get('location', '').strip()
            phone = request.form.get('phone', '').strip()

            db.add_doc('users', {
                'fullname': fullname,
                'username': username,
                'password': password,
                'category': category,
                'location': location,
                'phone': phone
            })
            flash(f'User "{username}" created.', 'success')

        elif action == 'edit':
            uid = request.form.get('uid')
            fullname = request.form.get('fullname', '').strip()
            username = request.form.get('username', '').strip()
            new_password = request.form.get('password', '').strip()
            category = request.form.get('category', 'USER')
            location = request.form.get('location', '').strip()
            phone = request.form.get('phone', '').strip()

            updates = {
                'fullname': fullname,
                'username': username,
                'category': category,
                'location': location,
                'phone': phone
            }
            if new_password:
                updates['password'] = new_password

            db.update_doc('users', uid, updates)

            # If editing self, update session
            if uid == session.get('user_id'):
                session['fullname'] = fullname
                session['username'] = username
                session['category'] = category

            flash(f'User "{username}" account updated.', 'success')

        elif action == 'delete':
            uid = request.form.get('uid')
            db.delete_doc('users', uid)
            flash('User deleted.', 'info')

        return redirect(url_for('users'))

    users_list = db.get_collection('users')
    return render_template('users.html', users=users_list)

if __name__ == '__main__':
    print("Starting Electronics Shop Inventory & Repair Management System...")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(host='0.0.0.0', port=5000, debug=True)
