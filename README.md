# Electronics Shop Inventory & Repair Management System

A modern **Python Flask Web Application** powered by **Firebase NoSQL (Firestore / Realtime Database)** designed specifically for Electronics Sales, Component Inventory, and Repair Service Shops (TVs, Laptops, Computers, Smartphones & Component Repair).

---

## ⚡ Key Features

- **🔧 Electronics Repair & Service Management**:
  - Track repair tickets for Smart TVs, Laptops, Computers, Smartphones, and Components.
  - Track Customer info, Problem descriptions, Serial numbers, and Assigned Technicians.
  - Track Estimated Repair Costs, Advance Payments, and Balance Due.
  - Real-time status workflow (`Received`, `Diagnosing`, `In Progress`, `Waiting for Parts`, `Ready for Pickup`, `Delivered`).
  - **Printable Service Receipts** for customers.

- **📦 Product Inventory & Stock Management**:
  - Catalogue electronics products and spare parts with cost and selling prices.
  - Low stock warning alerts (< 5 units).

- **🛒 Sales & Purchase Intake**:
  - Log wholesale stock intake from suppliers.
  - Process customer sales with automatic stock deduction and revenue analytics.

- **👥 Supplier & Customer Directories**:
  - Keep full contact directories for suppliers and customers.

- **🛡️ Multi-Role Security & Admin Panel**:
  - Session authentication with `ADMINISTRATOR` and `STAFF / TECHNICIAN` roles.

- **🔥 Hybrid Firebase / Offline NoSQL Engine**:
  - Connects to **Firebase Firestore** when `serviceAccountKey.json` is provided.
  - Seamlessly falls back to an offline local NoSQL engine for zero-install, out-of-the-box local operation.

---

## 🚀 How to Run (1-Click)

### Quick Start on Windows
Simply double-click [`run_flask.bat`](file:///d:/SHawon%20Bhaiya%20Soft/IMSsoft/run_flask.bat). It will start the server and automatically open `http://127.0.0.1:5000` in your browser.

### Manual Command Line Start
```cmd
cd /d "D:\SHawon Bhaiya Soft\IMSsoft"
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your web browser.

---

## 🔑 Default Login Credentials

- **Username**: `user4`
- **Password**: `user4`
- **Category**: `ADMINISTRATOR`

---

## 🔥 Firebase Setup (Optional)

To connect to a live Firebase project:
1. Go to [Firebase Console](https://console.firebase.google.com/).
2. Create a project and download your **Service Account Key JSON**.
3. Save the file as `serviceAccountKey.json` inside this root project folder (`D:\SHawon Bhaiya Soft\IMSsoft\serviceAccountKey.json`).
4. Restart the app (`run_flask.bat`). It will automatically connect to Firebase Firestore!
