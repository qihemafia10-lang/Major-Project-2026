"""
database.py
-----------
Manages all SQLite database operations for the Hotel Management System.
Provides the DatabaseManager class with methods for CRUD on all tables.
"""

import sqlite3
import os
from datetime import datetime
from utils import log_event, Colors

DB_PATH = os.path.join(os.path.dirname(__file__), "hotel.db")


class DatabaseManager:
    """
    Handles all interactions with the SQLite database.
    Uses context managers to ensure connections are properly closed.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._initialize_db()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        """Return a new database connection with row_factory set."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row          # rows accessible by column name
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize_db(self) -> None:
        """Create tables if they do not already exist."""
        ddl = """
        CREATE TABLE IF NOT EXISTS Rooms (
            room_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT    NOT NULL UNIQUE,
            room_type   TEXT    NOT NULL,
            price       REAL    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'Available'
        );

        CREATE TABLE IF NOT EXISTS Customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            phone       TEXT    NOT NULL UNIQUE,
            email       TEXT    NOT NULL,
            address     TEXT,
            id_proof    TEXT
        );

        CREATE TABLE IF NOT EXISTS Bookings (
            booking_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id    INTEGER NOT NULL,
            room_id        INTEGER NOT NULL,
            check_in       TEXT    NOT NULL,
            check_out      TEXT    NOT NULL,
            total_days     INTEGER NOT NULL,
            bill_amount    REAL    NOT NULL,
            booking_status TEXT    NOT NULL DEFAULT 'Confirmed',
            FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
            FOREIGN KEY (room_id)     REFERENCES Rooms(room_id)
        );

        CREATE TABLE IF NOT EXISTS AdminUsers (
            admin_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT    NOT NULL UNIQUE,
            password  TEXT    NOT NULL
        );
        """
        try:
            with self._connect() as conn:
                conn.executescript(ddl)
                # Insert default admin if none exists
                cur = conn.execute("SELECT COUNT(*) FROM AdminUsers")
                if cur.fetchone()[0] == 0:
                    conn.execute(
                        "INSERT INTO AdminUsers (username, password) VALUES (?, ?)",
                        ("admin", "admin123")
                    )
                conn.commit()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Database initialization failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Admin
    # ------------------------------------------------------------------

    def verify_admin(self, username: str, password: str) -> bool:
        """Return True if credentials match an AdminUsers record."""
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    "SELECT 1 FROM AdminUsers WHERE username=? AND password=?",
                    (username, password)
                )
                return cur.fetchone() is not None
        except sqlite3.Error as exc:
            raise RuntimeError(f"Admin verification error: {exc}") from exc

    # ------------------------------------------------------------------
    # Room CRUD
    # ------------------------------------------------------------------

    def add_room(self, room_number: str, room_type: str, price: float) -> int:
        """Insert a new room and return its generated room_id."""
        sql = "INSERT INTO Rooms (room_number, room_type, price) VALUES (?, ?, ?)"
        try:
            with self._connect() as conn:
                cur = conn.execute(sql, (room_number, room_type, price))
                conn.commit()
                return cur.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Room number '{room_number}' already exists.")
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error adding room: {exc}") from exc

    def get_all_rooms(self) -> list:
        """Return all room records as a list of Row objects."""
        try:
            with self._connect() as conn:
                return conn.execute("SELECT * FROM Rooms ORDER BY room_number").fetchall()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error fetching rooms: {exc}") from exc

    def get_available_rooms(self) -> list:
        """Return only rooms with status='Available'."""
        try:
            with self._connect() as conn:
                return conn.execute(
                    "SELECT * FROM Rooms WHERE status='Available' ORDER BY room_number"
                ).fetchall()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error fetching available rooms: {exc}") from exc

    def get_room_by_id(self, room_id: int):
        """Return a single room by its ID, or None."""
        try:
            with self._connect() as conn:
                return conn.execute(
                    "SELECT * FROM Rooms WHERE room_id=?", (room_id,)
                ).fetchone()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error fetching room: {exc}") from exc

    def get_room_by_number(self, room_number: str):
        """Return a single room by its room number, or None."""
        try:
            with self._connect() as conn:
                return conn.execute(
                    "SELECT * FROM Rooms WHERE room_number=?", (room_number,)
                ).fetchone()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error fetching room: {exc}") from exc

    def get_rooms_by_type(self, room_type: str) -> list:
        """Return rooms filtered by type (case-insensitive)."""
        try:
            with self._connect() as conn:
                return conn.execute(
                    "SELECT * FROM Rooms WHERE LOWER(room_type)=LOWER(?) ORDER BY room_number",
                    (room_type,)
                ).fetchall()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error fetching rooms by type: {exc}") from exc

    def get_rooms_by_max_price(self, max_price: float) -> list:
        """Return available rooms with price <= max_price."""
        try:
            with self._connect() as conn:
                return conn.execute(
                    "SELECT * FROM Rooms WHERE price<=? AND status='Available' ORDER BY price",
                    (max_price,)
                ).fetchall()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error filtering rooms by price: {exc}") from exc

    def update_room(self, room_id: int, room_number: str, room_type: str, price: float) -> bool:
        """Update room details. Returns True on success."""
        sql = "UPDATE Rooms SET room_number=?, room_type=?, price=? WHERE room_id=?"
        try:
            with self._connect() as conn:
                cur = conn.execute(sql, (room_number, room_type, price, room_id))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.IntegrityError:
            raise ValueError(f"Room number '{room_number}' already used by another room.")
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error updating room: {exc}") from exc

    def update_room_status(self, room_id: int, status: str) -> None:
        """Update only the status field of a room."""
        try:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE Rooms SET status=? WHERE room_id=?", (status, room_id)
                )
                conn.commit()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error updating room status: {exc}") from exc

    def delete_room(self, room_id: int) -> bool:
        """Delete a room by ID. Returns True if a row was deleted."""
        try:
            with self._connect() as conn:
                cur = conn.execute("DELETE FROM Rooms WHERE room_id=?", (room_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error deleting room: {exc}") from exc

    # ------------------------------------------------------------------
    # Customer CRUD
    # ------------------------------------------------------------------

    def add_customer(self, name: str, phone: str, email: str,
                     address: str, id_proof: str) -> int:
        """Insert a new customer and return the generated customer_id."""
        sql = ("INSERT INTO Customers (name, phone, email, address, id_proof) "
               "VALUES (?, ?, ?, ?, ?)")
        try:
            with self._connect() as conn:
                cur = conn.execute(sql, (name, phone, email, address, id_proof))
                conn.commit()
                return cur.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"A customer with phone '{phone}' already exists.")
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error adding customer: {exc}") from exc

    def get_all_customers(self) -> list:
        """Return all customer records."""
        try:
            with self._connect() as conn:
                return conn.execute("SELECT * FROM Customers ORDER BY name").fetchall()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error fetching customers: {exc}") from exc

    def get_customer_by_id(self, customer_id: int):
        """Return a single customer by ID, or None."""
        try:
            with self._connect() as conn:
                return conn.execute(
                    "SELECT * FROM Customers WHERE customer_id=?", (customer_id,)
                ).fetchone()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error fetching customer: {exc}") from exc

    def search_customer(self, keyword: str) -> list:
        """Search customers by name or phone (partial match)."""
        pattern = f"%{keyword}%"
        try:
            with self._connect() as conn:
                return conn.execute(
                    "SELECT * FROM Customers WHERE name LIKE ? OR phone LIKE ?",
                    (pattern, pattern)
                ).fetchall()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error searching customers: {exc}") from exc

    def update_customer(self, customer_id: int, name: str, phone: str,
                        email: str, address: str, id_proof: str) -> bool:
        """Update customer details. Returns True on success."""
        sql = ("UPDATE Customers SET name=?, phone=?, email=?, address=?, id_proof=? "
               "WHERE customer_id=?")
        try:
            with self._connect() as conn:
                cur = conn.execute(sql, (name, phone, email, address, id_proof, customer_id))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.IntegrityError:
            raise ValueError(f"Phone '{phone}' is already used by another customer.")
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error updating customer: {exc}") from exc

    def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer by ID. Returns True if deleted."""
        try:
            with self._connect() as conn:
                cur = conn.execute("DELETE FROM Customers WHERE customer_id=?", (customer_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error deleting customer: {exc}") from exc

    # ------------------------------------------------------------------
    # Booking CRUD
    # ------------------------------------------------------------------

    def create_booking(self, customer_id: int, room_id: int,
                       check_in: str, check_out: str,
                       total_days: int, bill_amount: float) -> int:
        """Insert a new booking record and return its booking_id."""
        sql = ("INSERT INTO Bookings "
               "(customer_id, room_id, check_in, check_out, total_days, bill_amount) "
               "VALUES (?, ?, ?, ?, ?, ?)")
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    sql, (customer_id, room_id, check_in, check_out, total_days, bill_amount)
                )
                conn.commit()
                return cur.lastrowid
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error creating booking: {exc}") from exc

    def get_booking_by_id(self, booking_id: int):
        """Return a single booking with joined customer and room info, or None."""
        sql = """
            SELECT b.*,
                   c.name        AS customer_name,
                   c.phone       AS customer_phone,
                   c.email       AS customer_email,
                   r.room_number AS room_number,
                   r.room_type   AS room_type,
                   r.price       AS price_per_day
            FROM Bookings b
            JOIN Customers c ON b.customer_id = c.customer_id
            JOIN Rooms     r ON b.room_id     = r.room_id
            WHERE b.booking_id = ?
        """
        try:
            with self._connect() as conn:
                return conn.execute(sql, (booking_id,)).fetchone()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error fetching booking: {exc}") from exc

    def get_active_booking_for_room(self, room_id: int):
        """Return the active (Confirmed/Checked-In) booking for a room, or None."""
        try:
            with self._connect() as conn:
                return conn.execute(
                    "SELECT * FROM Bookings WHERE room_id=? AND booking_status IN ('Confirmed','Checked-In')",
                    (room_id,)
                ).fetchone()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error fetching booking for room: {exc}") from exc

    def get_all_bookings(self) -> list:
        """Return all bookings with joined customer and room details."""
        sql = """
            SELECT b.*,
                   c.name        AS customer_name,
                   r.room_number AS room_number,
                   r.room_type   AS room_type
            FROM Bookings b
            JOIN Customers c ON b.customer_id = c.customer_id
            JOIN Rooms     r ON b.room_id     = r.room_id
            ORDER BY b.booking_id DESC
        """
        try:
            with self._connect() as conn:
                return conn.execute(sql).fetchall()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error fetching bookings: {exc}") from exc

    def update_booking_status(self, booking_id: int, status: str) -> None:
        """Update the status of a booking."""
        try:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE Bookings SET booking_status=? WHERE booking_id=?",
                    (status, booking_id)
                )
                conn.commit()
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error updating booking status: {exc}") from exc

    # ------------------------------------------------------------------
    # Revenue / Statistics
    # ------------------------------------------------------------------

    def get_daily_revenue(self, date_str: str) -> float:
        """Return total revenue for bookings checked out on a given date (YYYY-MM-DD)."""
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    "SELECT COALESCE(SUM(bill_amount),0) FROM Bookings "
                    "WHERE check_out=? AND booking_status='Completed'",
                    (date_str,)
                )
                return cur.fetchone()[0]
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error computing daily revenue: {exc}") from exc

    def get_monthly_revenue(self, year: int, month: int) -> float:
        """Return total revenue for a given month (year, month as int)."""
        pattern = f"{year}-{month:02d}-%"
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    "SELECT COALESCE(SUM(bill_amount),0) FROM Bookings "
                    "WHERE check_out LIKE ? AND booking_status='Completed'",
                    (pattern,)
                )
                return cur.fetchone()[0]
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error computing monthly revenue: {exc}") from exc

    def get_dashboard_stats(self) -> dict:
        """Return a dict of summary statistics for the dashboard."""
        try:
            with self._connect() as conn:
                total_rooms    = conn.execute("SELECT COUNT(*) FROM Rooms").fetchone()[0]
                available      = conn.execute("SELECT COUNT(*) FROM Rooms WHERE status='Available'").fetchone()[0]
                booked         = conn.execute("SELECT COUNT(*) FROM Rooms WHERE status='Booked'").fetchone()[0]
                total_customers= conn.execute("SELECT COUNT(*) FROM Customers").fetchone()[0]
                total_bookings = conn.execute("SELECT COUNT(*) FROM Bookings").fetchone()[0]
                active_bookings= conn.execute(
                    "SELECT COUNT(*) FROM Bookings WHERE booking_status IN ('Confirmed','Checked-In')"
                ).fetchone()[0]
                total_revenue  = conn.execute(
                    "SELECT COALESCE(SUM(bill_amount),0) FROM Bookings WHERE booking_status='Completed'"
                ).fetchone()[0]
                return {
                    "total_rooms":     total_rooms,
                    "available_rooms": available,
                    "booked_rooms":    booked,
                    "total_customers": total_customers,
                    "total_bookings":  total_bookings,
                    "active_bookings": active_bookings,
                    "total_revenue":   total_revenue,
                }
        except sqlite3.Error as exc:
            raise RuntimeError(f"Error fetching dashboard stats: {exc}") from exc
