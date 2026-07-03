# 🏨 Hotel Management System

A **complete, menu-driven Hotel Management System** built in Python 3 following Object-Oriented Programming principles. Designed as a college-level project demonstrating OOP, SQLite, file handling, and exception handling.

---

## 📋 Features

| Category | Features |
|---|---|
| **Room Management** | View all / available rooms, Add, Update, Delete, Search by type, Filter by price |
| **Customer Management** | Add, View, Search, Update, Delete customers |
| **Reservations** | Book room, Check-In, Check-Out, Booking History |
| **Billing** | Generate & save invoice (with 10% tax), Daily/Monthly revenue reports |
| **Dashboard** | Real-time statistics (rooms, customers, revenue) |
| **Security** | Password-protected admin login |
| **Logs** | All events recorded to `logs.txt` |

---

## 🏗️ Project Structure

```
hotel_management/
│
├── main.py          # Entry point — menu loop & admin login
├── database.py      # DatabaseManager — all SQLite CRUD
├── models.py        # OOP models: Room, Customer, Booking, Billing
├── hotel.py         # Hotel class — business logic
├── billing.py       # BillingManager — invoice generation
├── utils.py         # Validators, coloured output, logging helpers
├── requirements.txt
├── README.md
│
invoices/            # Auto-created — Invoice_XXXX.txt files
logs.txt             # Auto-created — event log
hotel.db             # Auto-created — SQLite database
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.9+
- `colorama` package

### Steps

```bash
# Clone / download the project
cd hotel_management

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## 🚀 How to Run

```bash
python main.py
```

**Default Admin Credentials**

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin123` |

---

## 🗃️ Database Schema

### Rooms
| Column | Type | Notes |
|---|---|---|
| room_id | INTEGER | Primary Key, Auto-increment |
| room_number | TEXT | Unique |
| room_type | TEXT | Single / Double / Suite / Deluxe / Penthouse |
| price | REAL | Price per night |
| status | TEXT | Available / Booked |

### Customers
| Column | Type | Notes |
|---|---|---|
| customer_id | INTEGER | Primary Key |
| name | TEXT | Full name |
| phone | TEXT | Unique, digits only |
| email | TEXT | Validated format |
| address | TEXT | Optional |
| id_proof | TEXT | Aadhar / Passport / DL |

### Bookings
| Column | Type | Notes |
|---|---|---|
| booking_id | INTEGER | Primary Key |
| customer_id | INTEGER | FK → Customers |
| room_id | INTEGER | FK → Rooms |
| check_in | TEXT | YYYY-MM-DD |
| check_out | TEXT | YYYY-MM-DD |
| total_days | INTEGER | Auto-calculated |
| bill_amount | REAL | Base amount (excl. tax) |
| booking_status | TEXT | Confirmed / Checked-In / Completed |

---

## 📄 Invoice Example

```
====================================================
             Grand Horizon Hotel
          OFFICIAL INVOICE / RECEIPT
====================================================
 Invoice No  : INV-0001
 Date Issued : 2025-01-15 10:30:00
----------------------------------------------------
 GUEST INFORMATION
----------------------------------------------------
 Customer ID  : 1
 Name         : John Doe
 Phone        : 9876543210
 Email        : john@example.com
----------------------------------------------------
 ROOM INFORMATION
----------------------------------------------------
 Room Number  : 101
 Room Type    : Deluxe
 Check-In     : 2025-01-10
 Check-Out    : 2025-01-15
 Total Days   : 5
----------------------------------------------------
 BILLING SUMMARY
----------------------------------------------------
 Price / Day  : ₹  3000.00
 Base Amount  : ₹ 15000.00
 Tax (10 %)   : ₹  1500.00
 GRAND TOTAL  : ₹ 16500.00
====================================================
```

---

## 🖼️ Screenshots

> *(Add screenshots here after running the application)*

---

## ✅ Validations

- Phone: 7–15 digits only
- Email: standard format check
- Check-out must be after check-in
- Cannot book an already booked room
- Cannot delete a booked room
- Duplicate phone numbers rejected

---

## 🔮 Future Improvements

- [ ] Web interface (Flask / Django)
- [ ] PDF invoice generation (ReportLab)
- [ ] Email invoice to customer (smtplib)
- [ ] Room photo uploads
- [ ] Multi-user role system (Admin / Receptionist)
- [ ] Export reports to Excel (openpyxl)
- [ ] Online payment integration

---

## 📚 Concepts Demonstrated

- **OOP**: Classes, constructors, methods, class methods, encapsulation
- **SQLite**: CRUD operations, foreign keys, aggregation queries
- **File Handling**: Invoice text files, event log (`logs.txt`)
- **Exception Handling**: try/except/finally, custom error messages
- **Colorama**: Coloured terminal output for professional UX

---

*Developed as a college-level Python project demonstrating core software engineering principles.*
