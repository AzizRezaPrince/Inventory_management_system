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

def log_activity(action_type, title, description, target_ref=""):
    try:
        user_name = session.get('fullname') or session.get('username') or 'System'
        user_role = session.get('category') or 'TECHNICIAN'
        db.add_doc('activity_logs', {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user': user_name,
            'user_role': user_role,
            'action_type': action_type,
            'title': title,
            'description': description,
            'target_ref': target_ref
        })
    except Exception as ex:
        print(f"Error logging activity: {ex}")

# --- Routes ---

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('category') == 'TECHNICIAN':
            return redirect(url_for('repairs'))
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
            session['category'] = user.get('category', 'TECHNICIAN')
            
            log_activity('LOGIN', 'User Signed In', f"{user.get('fullname')} ({user.get('category')}) logged in successfully.")

            flash(f"Welcome back, {user.get('fullname')}!", 'success')
            if user.get('category') == 'TECHNICIAN':
                return redirect(url_for('repairs'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    log_activity('LOGOUT', 'User Signed Out', f"{session.get('fullname', 'User')} logged out.")
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('category') == 'TECHNICIAN':
        flash('Technicians are directed straight to the Electronics Repair Services Workspace.', 'info')
        return redirect(url_for('repairs'))

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
    
    # Cost & Name Maps for products
    cost_map = {p.get('productcode'): float(p.get('costprice', 0)) for p in products}
    product_name_map = {p.get('productcode'): p.get('productname', 'Item') for p in products}

    # Revenue Calculation
    total_revenue = sum(float(s.get('revenue', 0)) for s in sales)
    
    # Dates for Monthly & Yearly Analysis
    now = datetime.now()
    curr_year = now.year
    curr_month_str = now.strftime('%Y-%m')
    curr_year_str = str(curr_year)
    prev_year_str = str(curr_year - 1)

    # Monthly & Yearly Analytics Initializers
    monthly_sales_rev = 0.0
    monthly_sales_cost = 0.0
    monthly_sales_count = 0

    yearly_sales_rev = 0.0
    prev_year_sales_rev = 0.0

    # Sales by Product / Category for Pie Chart
    sales_by_product = {}

    # Monthly Trend (12 Months of Current Year)
    months_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_sales_trend = [0.0] * 12
    monthly_repair_trend = [0.0] * 12
    monthly_profit_trend = [0.0] * 12

    for s in sales:
        s_date_str = str(s.get('date', ''))
        rev = float(s.get('revenue', 0))
        qty = int(s.get('quantity', 1))
        pcode = s.get('productcode')
        pname = product_name_map.get(pcode, pcode or 'Product Item')
        cprice = cost_map.get(pcode, 0.0) * qty

        sales_by_product[pname] = sales_by_product.get(pname, 0.0) + rev

        if s_date_str.startswith(curr_month_str):
            monthly_sales_rev += rev
            monthly_sales_cost += cprice
            monthly_sales_count += qty
        
        if s_date_str.startswith(curr_year_str):
            yearly_sales_rev += rev
            try:
                dt = datetime.strptime(s_date_str[:10], '%Y-%m-%d')
                m_idx = dt.month - 1
                monthly_sales_trend[m_idx] += rev
                monthly_profit_trend[m_idx] += (rev - cprice)
            except Exception:
                pass
        elif s_date_str.startswith(prev_year_str):
            prev_year_sales_rev += rev

    monthly_sales_profit = monthly_sales_rev - monthly_sales_cost

    # Repairs Analytics
    monthly_repair_rev = 0.0
    monthly_repair_count = 0
    yearly_repair_rev = 0.0
    prev_year_repair_rev = 0.0

    repair_status_counts = {
        'Received': 0,
        'Diagnosing': 0,
        'In Progress': 0,
        'Ready for Delivery': 0,
        'Delivered': 0
    }
    repair_device_counts = {}

    active_repairs = []
    for r in repairs:
        status = r.get('status', 'Received')
        if status in repair_status_counts:
            repair_status_counts[status] += 1
        else:
            repair_status_counts[status] = 1

        dtype = r.get('device_type', 'Other')
        if dtype:
            repair_device_counts[dtype] = repair_device_counts.get(dtype, 0) + 1

        if status not in ['Delivered', 'Cancelled']:
            active_repairs.append(r)

        r_date_str = str(r.get('created_at', ''))
        est_cost = float(r.get('estimated_cost', 0))

        if r_date_str.startswith(curr_month_str):
            monthly_repair_rev += est_cost
            monthly_repair_count += 1

        if r_date_str.startswith(curr_year_str):
            yearly_repair_rev += est_cost
            try:
                dt = datetime.strptime(r_date_str[:10], '%Y-%m-%d')
                m_idx = dt.month - 1
                monthly_repair_trend[m_idx] += est_cost
                monthly_profit_trend[m_idx] += est_cost
            except Exception:
                pass
        elif r_date_str.startswith(prev_year_str):
            prev_year_repair_rev += est_cost

    pending_repair_count = len(active_repairs)

    # Expenses Analytics
    expenses = db.get_collection('expenses')
    monthly_total_expenses = sum(float(e.get('amount', 0)) for e in expenses if str(e.get('date', '')).startswith(curr_month_str))

    # Subtract Expenses for 12 months trend profit calculation
    for e in expenses:
        e_date_str = str(e.get('date', ''))
        e_amt = float(e.get('amount', 0))
        if e_date_str.startswith(curr_year_str):
            try:
                dt = datetime.strptime(e_date_str[:10], '%Y-%m-%d')
                m_idx = dt.month - 1
                monthly_profit_trend[m_idx] -= e_amt
            except Exception:
                pass

    # Monthly Totals
    monthly_total_revenue = monthly_sales_rev + monthly_repair_rev
    monthly_total_profit = (monthly_sales_profit + monthly_repair_rev) - monthly_total_expenses

    # Yearly Growth Calculation
    yearly_total_revenue = yearly_sales_rev + yearly_repair_rev
    prev_year_total_revenue = prev_year_sales_rev + prev_year_repair_rev
    
    if prev_year_total_revenue > 0:
        yearly_growth_pct = ((yearly_total_revenue - prev_year_total_revenue) / prev_year_total_revenue) * 100.0
    else:
        yearly_growth_pct = 100.0 if yearly_total_revenue > 0 else 0.0

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

    # Prepare Data for Chart.js Pie Charts
    # 1. Sales Pie Chart (Top Products / Brands)
    sales_pie_labels = list(sales_by_product.keys())[:5] if sales_by_product else ['No Sales Logged']
    sales_pie_data = [sales_by_product[k] for k in sales_pie_labels] if sales_by_product else [0]

    # 2. Repair Pie Chart (By Status)
    repair_pie_labels = [k for k, v in repair_status_counts.items() if v > 0] or list(repair_status_counts.keys())
    repair_pie_data = [repair_status_counts[k] for k in repair_pie_labels]

    return render_template(
        'dashboard.html',
        total_products=total_products,
        total_stock_count=total_stock_count,
        total_suppliers=total_suppliers,
        total_revenue=total_revenue,
        pending_repair_count=pending_repair_count,
        active_repairs=active_repairs[:5],
        low_stock_list=low_stock_list,
        # Monthly Overview
        monthly_total_revenue=monthly_total_revenue,
        monthly_total_profit=monthly_total_profit,
        monthly_total_expenses=monthly_total_expenses,
        monthly_sales_rev=monthly_sales_rev,
        monthly_sales_count=monthly_sales_count,
        monthly_repair_rev=monthly_repair_rev,
        monthly_repair_count=monthly_repair_count,
        # Yearly Growth
        yearly_total_revenue=yearly_total_revenue,
        prev_year_total_revenue=prev_year_total_revenue,
        yearly_growth_pct=yearly_growth_pct,
        curr_year=curr_year,
        # Chart Data
        months_labels=months_labels,
        monthly_sales_trend=monthly_sales_trend,
        monthly_repair_trend=monthly_repair_trend,
        monthly_profit_trend=monthly_profit_trend,
        sales_pie_labels=sales_pie_labels,
        sales_pie_data=sales_pie_data,
        repair_pie_labels=repair_pie_labels,
        repair_pie_data=repair_pie_data,
        repair_device_labels=list(repair_device_counts.keys()) or ['No Repairs Logged'],
        repair_device_data=list(repair_device_counts.values()) or [0]
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

def generate_product_code_by_category(category_name, products_list):
    cat_upper = (category_name or '').upper()
    if 'TV' in cat_upper or 'DISPLAY' in cat_upper or 'MONITOR' in cat_upper:
        prefix = 'TV'
    elif 'LAPTOP' in cat_upper or 'NOTEBOOK' in cat_upper:
        prefix = 'LAP'
    elif 'DESKTOP' in cat_upper or 'COMPUTER' in cat_upper or 'PC' in cat_upper:
        prefix = 'PC'
    elif 'MOBILE' in cat_upper or 'PHONE' in cat_upper or 'SMARTPHONE' in cat_upper or 'TABLET' in cat_upper:
        prefix = 'MOB'
    elif 'AUDIO' in cat_upper or 'SPEAKER' in cat_upper or 'SOUND' in cat_upper:
        prefix = 'AUD'
    elif 'PART' in cat_upper or 'COMPONENT' in cat_upper or 'IC' in cat_upper or 'BOARD' in cat_upper:
        prefix = 'CMP'
    else:
        prefix = 'PRD'

    today_str = datetime.now().strftime('%d%m%Y')
    full_prefix = f"{prefix}-{today_str}"
    
    matching_codes = [p.get('productcode', '') for p in products_list if str(p.get('productcode', '')).startswith(full_prefix)]
    next_num = len(matching_codes) + 1
    return f"{full_prefix}-{next_num:03d}"

# --- Product Inventory Management ---

@app.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            pcode = request.form.get('productcode', '').strip()
            pname = request.form.get('productname', '').strip()
            category = request.form.get('category', 'General Electronics').strip()
            brand = request.form.get('brand', '').strip() or 'General'
            cost = float(request.form.get('costprice', 0))
            sell = float(request.form.get('sellingprice', 0))
            init_qty = int(request.form.get('initial_quantity', 0))

            products_list = db.get_collection('products')

            # Auto-generate next code by category if not provided or default
            if not pcode:
                pcode = generate_product_code_by_category(category, products_list)

            doc_id = db.add_doc('products', {
                'productcode': pcode,
                'productname': pname,
                'category': category,
                'brand': brand,
                'costprice': cost,
                'sellingprice': sell
            })
            db.update_stock(pcode, init_qty)
            flash(f'Product "{pname}" added with category code [{pcode}] and {init_qty} stock units!', 'success')

        elif action == 'edit':
            pid = request.form.get('pid')
            pcode = request.form.get('productcode', '').strip()
            pname = request.form.get('productname', '').strip()
            category = request.form.get('category', 'General Electronics').strip()
            brand = request.form.get('brand', '').strip()
            cost = float(request.form.get('costprice', 0))
            sell = float(request.form.get('sellingprice', 0))

            db.update_doc('products', pid, {
                'productcode': pcode,
                'productname': pname,
                'category': category,
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

    # Default next product code (General PRD prefix)
    next_product_code = generate_product_code_by_category('General Electronics', products_list)

    return render_template('products.html', products=products_list, next_product_code=next_product_code)

# --- Electronics Repair & Service Management ---

@app.route('/repairs', methods=['GET', 'POST'])
@login_required
def repairs():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            today_str = datetime.now().strftime('%d%m%Y')
            prefix = f"SRV-{today_str}"
            repairs_list = db.get_collection('repairs')
            today_repairs = [r for r in repairs_list if str(r.get('id', '')).startswith(prefix)]
            next_num = len(today_repairs) + 1
            ticket_id = f"{prefix}-{next_num:03d}"

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
            log_activity('REPAIR_CREATE', f'Created Repair Ticket #{ticket_id}', f'Ticket for {cname} ({dtype} - {issue}) assigned to {repair_item["technician"]}', target_ref=ticket_id)
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
                log_activity('REPAIR_STATUS', f'Updated Repair Ticket #{ticket_id}', f'Status updated to "{new_status}" (Total Cost: Tk {curr_cost:.2f})', target_ref=ticket_id)
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
            location = request.form.get('location', '').strip() or 'Dhaka'
            phone = request.form.get('phone', '').strip() or 'N/A'

            suppliers_list = db.get_collection('suppliers')
            if not scode:
                existing_codes = [s.get('suppliercode', '') for s in suppliers_list]
                max_num = 1000
                for code in existing_codes:
                    if str(code).startswith('SUP-'):
                        try:
                            num = int(str(code).split('SUP-')[1])
                            if num > max_num: max_num = num
                        except ValueError:
                            pass
                scode = f"SUP-{max_num + 1}"

            db.add_doc('suppliers', {
                'suppliercode': scode,
                'fullname': fname,
                'location': location,
                'phone': phone
            })
            flash(f'Supplier "{fname}" added to database with code [{scode}].', 'success')

        elif action == 'delete':
            sid = request.form.get('sid')
            db.delete_doc('suppliers', sid)
            flash('Supplier deleted.', 'info')

        return redirect(url_for('suppliers'))

    suppliers_list = db.get_collection('suppliers')
    purchases_list = db.get_collection('purchaseinfo')

    # Auto-sync missing suppliers from stock purchase records!
    newly_added = False
    existing_names = {s.get('fullname', '').strip().lower() for s in suppliers_list}
    
    for pur in purchases_list:
        sname = pur.get('suppliercode', '').strip()
        if sname and sname.lower() != 'general supplier' and sname.lower() not in existing_names:
            sphone = pur.get('supplier_phone', 'N/A')
            db.ensure_supplier_exists(sname, phone=sphone, location='Dhaka')
            existing_names.add(sname.lower())
            newly_added = True

    if newly_added:
        suppliers_list = db.get_collection('suppliers')

    # Calculate financial & purchase history for each supplier
    supplier_stats = {}
    for pur in purchases_list:
        sname_key = pur.get('suppliercode', '').strip().lower()
        if sname_key not in supplier_stats:
            supplier_stats[sname_key] = {
                'count': 0,
                'volume': 0.0,
                'paid': 0.0,
                'due': 0.0
            }
        supplier_stats[sname_key]['count'] += 1
        total_c = float(pur.get('totalcost', 0))
        paid_a = float(pur.get('paid_amount', total_c))
        due_a = float(pur.get('due_amount', max(0.0, total_c - paid_a)))
        
        supplier_stats[sname_key]['volume'] += total_c
        supplier_stats[sname_key]['paid'] += paid_a
        supplier_stats[sname_key]['due'] += due_a

    for s in suppliers_list:
        skey = s.get('fullname', '').strip().lower()
        stats = supplier_stats.get(skey, {'count': 0, 'volume': 0.0, 'paid': 0.0, 'due': 0.0})
        s['intake_count'] = stats['count']
        s['total_volume'] = stats['volume']
        s['total_paid'] = stats['paid']
        s['total_due'] = stats['due']

    # Auto-generate next supplier code
    existing_codes = [s.get('suppliercode', '') for s in suppliers_list]
    max_num = 1000
    for code in existing_codes:
        if str(code).startswith('SUP-'):
            try:
                num = int(str(code).split('SUP-')[1])
                if num > max_num: max_num = num
            except ValueError:
                pass
    next_supplier_code = f"SUP-{max_num + 1}"

    total_due_all = sum(float(s.get('total_due', 0)) for s in suppliers_list)

    return render_template(
        'suppliers.html',
        suppliers=suppliers_list,
        next_supplier_code=next_supplier_code,
        total_due_all=total_due_all
    )

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
        action = request.form.get('action', 'add')

        if action == 'add':
            supplier_input = request.form.get('supplier_input', '').strip() or 'General Supplier'
            supplier_phone = request.form.get('supplier_phone', '').strip() or 'N/A'
            supplier_location = request.form.get('supplier_location', '').strip() or 'Dhaka'
            
            pselect_mode = request.form.get('product_select_mode', 'existing')
            pcode = request.form.get('productcode', '').strip()
            pname = request.form.get('productname', '').strip()
            category = request.form.get('category', 'General Electronics').strip()
            brand = request.form.get('brand', '').strip() or 'General'
            
            cost_price = float(request.form.get('cost_price', 0))
            selling_price = float(request.form.get('selling_price', 0))
            qty = int(request.form.get('quantity', 1))
            
            total_cost_input = request.form.get('totalcost', '').strip()
            if total_cost_input and float(total_cost_input) > 0:
                total_cost = float(total_cost_input)
            else:
                total_cost = cost_price * qty

            paid_amount_input = request.form.get('paid_amount', '').strip()
            if paid_amount_input != '':
                paid_amount = float(paid_amount_input)
            else:
                paid_amount = total_cost

            due_amount = max(0.0, total_cost - paid_amount)
            payment_status = 'Paid' if due_amount <= 0 else 'Due Pending'

            # 1. Auto-sync Supplier into DB
            db.ensure_supplier_exists(supplier_input, supplier_phone, supplier_location)

            # 2. Automatic Product Registration & Stock Sync in Inventory!
            products_list = db.get_collection('products')
            existing_product = None
            if pcode and pcode != 'NEW_PRODUCT':
                for p in products_list:
                    if p.get('productcode') == pcode:
                        existing_product = p
                        break

            if not existing_product and pname:
                for p in products_list:
                    if p.get('productname', '').strip().lower() == pname.lower():
                        existing_product = p
                        pcode = p.get('productcode')
                        break

            if not existing_product:
                # REGISTER NEW PRODUCT AUTOMATICALLY INTO INVENTORY!
                if not pcode or pcode == 'NEW_PRODUCT':
                    pcode = generate_product_code_by_category(category, products_list)

                db.add_doc('products', {
                    'productcode': pcode,
                    'productname': pname or f"Stock Item {pcode}",
                    'category': category,
                    'brand': brand,
                    'costprice': cost_price,
                    'sellingprice': selling_price
                })
                db.update_stock(pcode, qty)
                flash(f'New Product "{pname or pcode}" registered in Inventory automatically with code [{pcode}] & {qty} units stock!', 'success')
            else:
                pcode = existing_product.get('productcode')
                db.update_stock(pcode, qty)
                updates = {}
                if cost_price > 0: updates['costprice'] = cost_price
                if selling_price > 0: updates['sellingprice'] = selling_price
                if category: updates['category'] = category
                if updates:
                    db.update_doc('products', existing_product.get('id'), updates)
                flash(f'Stock for product "{existing_product.get("productname", pcode)}" increased by {qty} units!', 'success')

            # 3. Save Purchase Document
            purchase_doc = {
                'suppliercode': supplier_input,
                'supplier_phone': supplier_phone,
                'productcode': pcode,
                'productname': pname or (existing_product.get('productname') if existing_product else pcode),
                'category': category,
                'brand': brand,
                'quantity': qty,
                'cost_price': cost_price,
                'selling_price': selling_price,
                'totalcost': total_cost,
                'paid_amount': paid_amount,
                'due_amount': due_amount,
                'payment_status': payment_status,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'logged_by': session.get('fullname', 'System')
            }
            pid = db.add_doc('purchaseinfo', purchase_doc)

            # 4. AUTO-SYNC TO EXPENSES!
            db.add_doc('expenses', {
                'title': f"Stock Purchase ({qty} units x {purchase_doc['productname']})",
                'category': 'Stock Purchase (স্টক ক্রয়)',
                'amount': paid_amount if paid_amount > 0 else total_cost,
                'date': purchase_doc['date'],
                'reference_id': pid,
                'notes': f"Supplier: {supplier_input} | Total: Tk {total_cost:.2f}, Paid: Tk {paid_amount:.2f}, Due: Tk {due_amount:.2f}",
                'created_by': session.get('fullname', 'System'),
                'is_auto': True
            })

        elif action == 'update_payment':
            pur_id = request.form.get('pur_id')
            add_paid = float(request.form.get('additional_paid', 0))
            
            pur_doc = db.get_doc('purchaseinfo', pur_id)
            if pur_doc:
                curr_paid = float(pur_doc.get('paid_amount', 0)) + add_paid
                total_c = float(pur_doc.get('totalcost', 0))
                new_due = max(0.0, total_c - curr_paid)
                new_status = 'Paid' if new_due <= 0 else 'Due Pending'

                db.update_doc('purchaseinfo', pur_id, {
                    'paid_amount': curr_paid,
                    'due_amount': new_due,
                    'payment_status': new_status
                })

                # Log expense for additional paid amount
                db.add_doc('expenses', {
                    'title': f"Supplier Due Payment ({pur_doc.get('productname', 'Stock Item')})",
                    'category': 'Stock Purchase (স্টক ক্রয়)',
                    'amount': add_paid,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'reference_id': pur_id,
                    'notes': f"Supplier: {pur_doc.get('suppliercode')} | Cleared Due Payment: Tk {add_paid:.2f}",
                    'created_by': session.get('fullname', 'System'),
                    'is_auto': True
                })
                flash(f'Payment of Tk {add_paid:.2f} logged for Supplier. Remaining Due: Tk {new_due:.2f}', 'success')

        return redirect(url_for('purchases'))

    purchases_list = db.get_collection('purchaseinfo')
    purchases_list.sort(key=lambda x: str(x.get('date', '')), reverse=True)
    
    suppliers_list = db.get_collection('suppliers')
    products_list = db.get_collection('products')

    total_purchase_cost = sum(float(p.get('totalcost', 0)) for p in purchases_list)
    total_purchase_paid = sum(float(p.get('paid_amount', p.get('totalcost', 0))) for p in purchases_list)
    total_purchase_due = sum(float(p.get('due_amount', 0)) for p in purchases_list)

    return render_template(
        'purchases.html',
        purchases=purchases_list,
        suppliers=suppliers_list,
        products=products_list,
        total_purchase_cost=total_purchase_cost,
        total_purchase_paid=total_purchase_paid,
        total_purchase_due=total_purchase_due
    )

# --- Expenses Management ---

@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    if session.get('category') == 'TECHNICIAN':
        flash('Access Restricted: Expense Tracker is for Administrators only.', 'danger')
        return redirect(url_for('repairs'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            title = request.form.get('title', '').strip() or 'Shop Expense'
            category = request.form.get('category', 'Miscellaneous / Other (অন্যান্য)').strip()
            amount = float(request.form.get('amount', 0))
            exp_date = request.form.get('date', '').strip()
            notes = request.form.get('notes', '').strip()

            if not exp_date:
                exp_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            db.add_doc('expenses', {
                'title': title,
                'category': category,
                'amount': amount,
                'date': exp_date,
                'notes': notes,
                'created_by': session.get('fullname', 'Staff'),
                'is_auto': False
            })
            log_activity('EXPENSE_ADD', f'Logged Expense: {title}', f'Amount: Tk {amount:.2f} ({category})')
            flash(f'Expense "{title}" of Tk {amount:.2f} saved successfully!', 'success')

        elif action == 'delete':
            eid = request.form.get('eid')
            db.delete_doc('expenses', eid)
            log_activity('EXPENSE_DELETE', 'Deleted Expense Record', f'Deleted expense ID #{eid}')
            flash('Expense record deleted.', 'info')

        return redirect(url_for('expenses'))

    expenses_list = db.get_collection('expenses')
    
    # Auto-sync legacy purchaseinfo records to expenses if missing
    purchases_list = db.get_collection('purchaseinfo')
    synced_refs = {str(e.get('reference_id')) for e in expenses_list if e.get('reference_id')}
    
    products = db.get_collection('products')
    p_map = {p.get('productcode'): p.get('productname') for p in products}

    newly_synced = False
    for pur in purchases_list:
        pur_id = str(pur.get('id', ''))
        if pur_id and pur_id not in synced_refs:
            pcode = pur.get('productcode', 'Item')
            pname = p_map.get(pcode, pcode)
            qty = pur.get('quantity', 0)
            tcost = float(pur.get('totalcost', 0))
            pdate = pur.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            sinput = pur.get('suppliercode', 'Supplier')

            db.add_doc('expenses', {
                'title': f"Stock Purchase ({qty} units x {pname})",
                'category': 'Stock Purchase (স্টক ক্রয়)',
                'amount': tcost,
                'date': pdate,
                'reference_id': pur_id,
                'notes': f"Auto-synced from Stock Intake (Supplier: {sinput})",
                'created_by': 'System',
                'is_auto': True
            })
            newly_synced = True

    if newly_synced:
        expenses_list = db.get_collection('expenses')

    expenses_list.sort(key=lambda x: str(x.get('date', '')), reverse=True)

    # Compute Summaries
    now = datetime.now()
    curr_month_str = now.strftime('%Y-%m')

    total_expense_all_time = sum(float(e.get('amount', 0)) for e in expenses_list)
    monthly_expenses = sum(float(e.get('amount', 0)) for e in expenses_list if str(e.get('date', '')).startswith(curr_month_str))
    
    rent_expenses = sum(float(e.get('amount', 0)) for e in expenses_list if str(e.get('date', '')).startswith(curr_month_str) and 'Rent' in e.get('category', ''))
    utility_expenses = sum(float(e.get('amount', 0)) for e in expenses_list if str(e.get('date', '')).startswith(curr_month_str) and 'Utility' in e.get('category', ''))
    stock_expenses = sum(float(e.get('amount', 0)) for e in expenses_list if str(e.get('date', '')).startswith(curr_month_str) and 'Stock' in e.get('category', ''))
    salary_expenses = sum(float(e.get('amount', 0)) for e in expenses_list if str(e.get('date', '')).startswith(curr_month_str) and 'Salary' in e.get('category', ''))
    other_expenses = monthly_expenses - (rent_expenses + utility_expenses + stock_expenses + salary_expenses)

    categories = [
        'Shop Rent (দোকান ভাড়া)',
        'Utility Bills (ইউটিলিটি বিল)',
        'Staff Salary (স্টাফ বেতন)',
        'Stock Purchase (স্টক ক্রয়)',
        'Shop Maintenance & Repair (রক্ষণাবেক্ষণ)',
        'Miscellaneous / Other (অন্যান্য)'
    ]

    return render_template(
        'expenses.html',
        expenses=expenses_list,
        total_expense_all_time=total_expense_all_time,
        monthly_expenses=monthly_expenses,
        rent_expenses=rent_expenses,
        utility_expenses=utility_expenses,
        stock_expenses=stock_expenses,
        salary_expenses=salary_expenses,
        other_expenses=other_expenses,
        categories=categories
    )

# --- Sales Logging & Reports ---

@app.route('/sales', methods=['GET', 'POST'])
@login_required
def sales():
    if request.method == 'POST':
        action = request.form.get('action', 'add')

        if action == 'add':
            pcode = request.form.get('productcode')
            cinput = request.form.get('customer_input', '').strip() or request.form.get('customercode', '').strip() or 'Walk-in Customer'
            qty = int(request.form.get('quantity', 0))
            
            curr_stock = db.get_stock(pcode)
            if qty > curr_stock:
                flash(f'Insufficient stock! Available: {curr_stock}, Requested: {qty}', 'danger')
                return redirect(url_for('sales'))

            # Auto-sync Customer into DB if new!
            db.ensure_customer_exists(cinput)

            custom_price_input = request.form.get('custom_selling_price', '').strip()

            products = db.get_collection('products')
            default_selling_price = 0
            for p in products:
                if p.get('productcode') == pcode:
                    default_selling_price = float(p.get('sellingprice', 0))
                    break

            if custom_price_input:
                try:
                    unit_price = float(custom_price_input)
                except ValueError:
                    unit_price = default_selling_price
            else:
                unit_price = default_selling_price

            revenue = unit_price * qty
            
            payment_type = request.form.get('payment_type', 'Full Payment').strip()
            paid_amount_input = request.form.get('paid_amount', '').strip()
            if paid_amount_input != '':
                paid_amount = float(paid_amount_input)
            else:
                paid_amount = revenue

            due_amount = max(0.0, revenue - paid_amount)
            if payment_type == 'EMI / Installment':
                payment_status = 'EMI Active' if due_amount > 0 else 'Fully Paid'
            else:
                payment_status = 'Fully Paid' if due_amount <= 0 else 'Customer Due'

            emi_months = int(request.form.get('emi_months', 6)) if payment_type == 'EMI / Installment' else 0
            monthly_installment = float(request.form.get('monthly_installment', 0)) if payment_type == 'EMI / Installment' else 0.0
            next_due_date = request.form.get('next_due_date', '').strip() if payment_type == 'EMI / Installment' else ''

            today_str = datetime.now().strftime('%d%m%Y')
            prefix = f"SLS-{today_str}"
            sales_list = db.get_collection('salesreport')
            today_sales = [s for s in sales_list if str(s.get('id', '')).startswith(prefix) or str(s.get('memo_code', '')).startswith(prefix)]
            next_num = len(today_sales) + 1
            sale_memo_code = f"{prefix}-{next_num:03d}"

            sale_doc = {
                'id': sale_memo_code,
                'memo_code': sale_memo_code,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'productcode': pcode,
                'customercode': cinput,
                'quantity': qty,
                'unit_price': unit_price,
                'revenue': revenue,
                'paid_amount': paid_amount,
                'due_amount': due_amount,
                'payment_type': payment_type,
                'payment_status': payment_status,
                'emi_months': emi_months,
                'monthly_installment': monthly_installment,
                'next_due_date': next_due_date,
                'soldby': session.get('username', 'user')
            }
            db.add_doc('salesreport', sale_doc)
            db.update_stock(pcode, -qty)
            
            log_activity('SALE_LOG', f'Processed Sale Memo #{sale_memo_code}', f'Sold {qty} units of {pcode} to {cinput} (Total: Tk {revenue:.2f}, Paid: Tk {paid_amount:.2f}, Due: Tk {due_amount:.2f})', target_ref=sale_memo_code)
            
            flash(f'Sale #{sale_memo_code} processed successfully! Paid: Tk {paid_amount:.2f}, Due: Tk {due_amount:.2f}', 'success')

        elif action == 'collect_due':
            sale_id = request.form.get('sale_id')
            add_paid = float(request.form.get('additional_paid', 0))
            
            sale_doc = db.get_doc('salesreport', sale_id)
            if sale_doc:
                curr_paid = float(sale_doc.get('paid_amount', 0)) + add_paid
                total_rev = float(sale_doc.get('revenue', 0))
                new_due = max(0.0, total_rev - curr_paid)
                new_status = 'Fully Paid' if new_due <= 0 else ('EMI Active' if sale_doc.get('payment_type') == 'EMI / Installment' else 'Customer Due')

                db.update_doc('salesreport', sale_id, {
                    'paid_amount': curr_paid,
                    'due_amount': new_due,
                    'payment_status': new_status
                })
                log_activity('SALE_DUE_COLLECT', f'Collected Customer Due for Sale #{sale_id}', f'Collected Tk {add_paid:.2f} from {sale_doc.get("customercode")}. Remaining Due: Tk {new_due:.2f}', target_ref=sale_id)
                flash(f'Collected Tk {add_paid:.2f} from customer. Remaining Due: Tk {new_due:.2f}', 'success')

        return redirect(url_for('sales'))

    sales_list = db.get_collection('salesreport')
    sales_list.sort(key=lambda x: str(x.get('date', '')), reverse=True)

    products_list = db.get_collection('products')
    customers_list = db.get_collection('customers')

    total_sales_revenue = sum(float(s.get('revenue', 0)) for s in sales_list)
    total_sales_paid = sum(float(s.get('paid_amount', s.get('revenue', 0))) for s in sales_list)
    total_sales_due = sum(float(s.get('due_amount', 0)) for s in sales_list)

    return render_template(
        'sales.html',
        sales=sales_list,
        products=products_list,
        customers=customers_list,
        total_sales_revenue=total_sales_revenue,
        total_sales_paid=total_sales_paid,
        total_sales_due=total_sales_due
    )

# --- User & Technician Management ---

@app.route('/users', methods=['GET', 'POST'])
@admin_required
def users():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            fullname = request.form.get('fullname', '').strip()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            category = request.form.get('category', 'TECHNICIAN').strip()
            location = request.form.get('location', '').strip() or 'Dhaka'
            phone = request.form.get('phone', '').strip() or 'N/A'

            # Check duplicate username
            existing = db.get_collection('users')
            for u in existing:
                if u.get('username', '').lower() == username.lower():
                    flash(f'Username "{username}" is already taken!', 'danger')
                    return redirect(url_for('users'))

            db.add_doc('users', {
                'fullname': fullname,
                'username': username,
                'password': password,
                'category': category,
                'location': location,
                'phone': phone
            })
            log_activity('USER_ADD', f'Added New {category}', f'Admin created account for {fullname} ({username}) as {category}')
            flash(f'User account "{fullname}" ({category}) created successfully!', 'success')

        elif action == 'edit':
            uid = request.form.get('uid')
            fullname = request.form.get('fullname', '').strip()
            username = request.form.get('username', '').strip()
            new_password = request.form.get('password', '').strip()
            category = request.form.get('category', 'TECHNICIAN').strip()
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

            log_activity('USER_EDIT', 'Updated User Account', f'Admin updated details for user {fullname} ({category})')
            flash(f'User account "{fullname}" updated successfully!', 'success')

        elif action == 'delete':
            uid = request.form.get('uid')
            if str(uid) == str(session.get('user_id')):
                flash('You cannot delete your own logged-in admin account!', 'danger')
                return redirect(url_for('users'))

            target_user = db.get_doc('users', uid)
            target_name = target_user.get('fullname', uid) if target_user else uid
            db.delete_doc('users', uid)
            log_activity('USER_DELETE', 'Deleted User Account', f'Admin deleted user account {target_name}')
            flash('User account deleted.', 'info')

        return redirect(url_for('users'))

    users_list = db.get_collection('users')
    tech_count = sum(1 for u in users_list if u.get('category') == 'TECHNICIAN')
    admin_count = sum(1 for u in users_list if u.get('category') == 'ADMINISTRATOR')

    return render_template(
        'users.html',
        users=users_list,
        tech_count=tech_count,
        admin_count=admin_count
    )

# --- Activity Audit Logs Management ---

@app.route('/activity_logs', methods=['GET', 'POST'])
@admin_required
def activity_logs():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'edit_log':
            log_id = request.form.get('log_id')
            user_val = request.form.get('user', '').strip()
            act_type = request.form.get('action_type', '').strip()
            title_val = request.form.get('title', '').strip()
            desc_val = request.form.get('description', '').strip()

            db.update_doc('activity_logs', log_id, {
                'user': user_val,
                'action_type': act_type,
                'title': title_val,
                'description': desc_val
            })
            log_activity('LOG_EDIT', f'Edited Activity Log #{log_id}', f'Admin edited log details for {user_val}')
            flash('Activity log entry updated successfully!', 'success')

        elif action == 'delete_log':
            log_id = request.form.get('log_id')
            db.delete_doc('activity_logs', log_id)
            log_activity('LOG_DELETE', 'Deleted Activity Log', f'Admin deleted activity log #{log_id}')
            flash('Activity log entry deleted.', 'info')

        return redirect(url_for('activity_logs'))

    logs_list = db.get_collection('activity_logs')
    logs_list.sort(key=lambda x: str(x.get('date', '')), reverse=True)

    tech_log_count = sum(1 for l in logs_list if l.get('user_role') == 'TECHNICIAN')
    admin_log_count = sum(1 for l in logs_list if l.get('user_role') == 'ADMINISTRATOR')

    return render_template(
        'activity_logs.html',
        logs=logs_list,
        tech_log_count=tech_log_count,
        admin_log_count=admin_log_count
    )

if __name__ == '__main__':
    print("Starting Electronics Shop Inventory & Repair Management System...")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(host='0.0.0.0', port=5000, debug=True)
