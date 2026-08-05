# Inventory Management System for Electronics Shop

A Java-based Desktop Application for managing stock, products, suppliers, customers, and sales reports for electronics shops.

## 🚀 Features

- **Product Management**: Add, update, and track items and stock levels.
- **Supplier & Customer Tracking**: Keep records of suppliers and customer info.
- **Purchase & Sales Reports**: Log stock intake and generate sales reports.
- **User Role Access**: Admin and user login authentication.

---

## 🛠️ Project Structure

```text
├── InventoryMangagementSystem.jar   # Main executable application
├── run.bat                          # One-click Windows launcher script
├── ims.sql                          # Database dump (MySQL)
├── README.TXT                       # Original build instructions
└── lib/                             # Required Java dependency libraries
    ├── AbsoluteLayout.jar
    ├── JTattoo-1.6.10.jar
    ├── jcalendar-1.4.jar
    └── mysql-connector-java-5.1.23-bin.jar
```

---

## 📋 How to Run

### Option 1: Quick Launch (Windows)
Double-click `run.bat` or run:
```cmd
run.bat
```

### Option 2: Command Line
```cmd
java -jar "InventoryMangagementSystem.jar"
```

---

## 🗄️ Database Setup

1. Start your local **MySQL Server** (via XAMPP, WAMP, or standalone MySQL).
2. Create a database named `ims`.
3. Import `ims.sql` into the `ims` database.
4. **Default Admin Login**:
   - **Username**: `user4`
   - **Category**: `ADMINISTRATOR`
