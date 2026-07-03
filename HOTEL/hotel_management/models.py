"""
models.py
---------
Defines the core OOP model classes used throughout the Hotel Management System.
These are plain Python objects (data-transfer objects) that hold structured data.
They are NOT mapped to the DB directly – that is handled by DatabaseManager.
"""

from datetime import datetime, date
from typing import Optional


# ---------------------------------------------------------------------------
# Room model
# ---------------------------------------------------------------------------

class Room:
    """Represents a hotel room."""

    VALID_TYPES = ("Single", "Double", "Suite", "Deluxe", "Penthouse")

    def __init__(
        self,
        room_id: int,
        room_number: str,
        room_type: str,
        price: float,
        status: str = "Available",
    ):
        self.room_id     = room_id
        self.room_number = room_number
        self.room_type   = room_type
        self.price       = price
        self.status      = status

    # ------------------------------------------------------------------
    # Class-level factory
    # ------------------------------------------------------------------

    @classmethod
    def from_row(cls, row) -> "Room":
        """Construct a Room from a sqlite3.Row object."""
        return cls(
            room_id     = row["room_id"],
            room_number = row["room_number"],
            room_type   = row["room_type"],
            price       = row["price"],
            status      = row["status"],
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        return self.status == "Available"

    def __repr__(self) -> str:
        return (
            f"Room(id={self.room_id}, number={self.room_number!r}, "
            f"type={self.room_type!r}, price={self.price:.2f}, status={self.status!r})"
        )


# ---------------------------------------------------------------------------
# Customer model
# ---------------------------------------------------------------------------

class Customer:
    """Represents a hotel guest / customer."""

    def __init__(
        self,
        customer_id: int,
        name: str,
        phone: str,
        email: str,
        address: str = "",
        id_proof: str = "",
    ):
        self.customer_id = customer_id
        self.name        = name
        self.phone       = phone
        self.email       = email
        self.address     = address
        self.id_proof    = id_proof

    @classmethod
    def from_row(cls, row) -> "Customer":
        """Construct a Customer from a sqlite3.Row object."""
        return cls(
            customer_id = row["customer_id"],
            name        = row["name"],
            phone       = row["phone"],
            email       = row["email"],
            address     = row["address"] or "",
            id_proof    = row["id_proof"] or "",
        )

    def __repr__(self) -> str:
        return (
            f"Customer(id={self.customer_id}, name={self.name!r}, "
            f"phone={self.phone!r}, email={self.email!r})"
        )


# ---------------------------------------------------------------------------
# Booking model
# ---------------------------------------------------------------------------

class Booking:
    """Represents a room booking."""

    DATE_FMT = "%Y-%m-%d"

    def __init__(
        self,
        booking_id: int,
        customer_id: int,
        room_id: int,
        check_in: str,
        check_out: str,
        total_days: int,
        bill_amount: float,
        booking_status: str = "Confirmed",
        # Optional joined fields
        customer_name: Optional[str] = None,
        customer_phone: Optional[str] = None,
        customer_email: Optional[str] = None,
        room_number: Optional[str] = None,
        room_type: Optional[str] = None,
        price_per_day: Optional[float] = None,
    ):
        self.booking_id     = booking_id
        self.customer_id    = customer_id
        self.room_id        = room_id
        self.check_in       = check_in
        self.check_out      = check_out
        self.total_days     = total_days
        self.bill_amount    = bill_amount
        self.booking_status = booking_status

        # Joined / computed fields
        self.customer_name  = customer_name
        self.customer_phone = customer_phone
        self.customer_email = customer_email
        self.room_number    = room_number
        self.room_type      = room_type
        self.price_per_day  = price_per_day

    @classmethod
    def from_row(cls, row) -> "Booking":
        """Construct a Booking from a sqlite3.Row (possibly with joined columns)."""
        keys = row.keys()
        return cls(
            booking_id     = row["booking_id"],
            customer_id    = row["customer_id"],
            room_id        = row["room_id"],
            check_in       = row["check_in"],
            check_out      = row["check_out"],
            total_days     = row["total_days"],
            bill_amount    = row["bill_amount"],
            booking_status = row["booking_status"],
            customer_name  = row["customer_name"]  if "customer_name"  in keys else None,
            customer_phone = row["customer_phone"] if "customer_phone" in keys else None,
            customer_email = row["customer_email"] if "customer_email" in keys else None,
            room_number    = row["room_number"]    if "room_number"    in keys else None,
            room_type      = row["room_type"]      if "room_type"      in keys else None,
            price_per_day  = row["price_per_day"]  if "price_per_day"  in keys else None,
        )

    def check_in_date(self) -> date:
        return datetime.strptime(self.check_in, self.DATE_FMT).date()

    def check_out_date(self) -> date:
        return datetime.strptime(self.check_out, self.DATE_FMT).date()

    def __repr__(self) -> str:
        return (
            f"Booking(id={self.booking_id}, customer_id={self.customer_id}, "
            f"room_id={self.room_id}, check_in={self.check_in!r}, "
            f"check_out={self.check_out!r}, status={self.booking_status!r})"
        )


# ---------------------------------------------------------------------------
# Billing model
# ---------------------------------------------------------------------------

class Billing:
    """
    Encapsulates billing calculations for a booking.
    Applies a configurable tax rate (default 10 %).
    """

    TAX_RATE = 0.10   # 10 %

    def __init__(self, booking: Booking):
        self.booking       = booking
        self.base_amount   = booking.bill_amount
        self.tax_amount    = round(self.base_amount * self.TAX_RATE, 2)
        self.grand_total   = round(self.base_amount + self.tax_amount, 2)

    def generate_invoice_text(self, hotel_name: str = "Grand Horizon Hotel") -> str:
        """Return a formatted invoice string ready to print or save."""
        b = self.booking
        separator  = "=" * 52
        line       = "-" * 52

        invoice = f"""
{separator}
           {hotel_name}
        OFFICIAL INVOICE / RECEIPT
{separator}
 Invoice No  : INV-{b.booking_id:04d}
 Date Issued : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{line}
 GUEST INFORMATION
{line}
 Customer ID  : {b.customer_id}
 Name         : {b.customer_name or 'N/A'}
 Phone        : {b.customer_phone or 'N/A'}
 Email        : {b.customer_email or 'N/A'}
{line}
 ROOM INFORMATION
{line}
 Room Number  : {b.room_number or 'N/A'}
 Room Type    : {b.room_type or 'N/A'}
 Check-In     : {b.check_in}
 Check-Out    : {b.check_out}
 Total Days   : {b.total_days}
{line}
 BILLING SUMMARY
{line}
 Price / Day  : ₹{b.price_per_day or (self.base_amount / b.total_days if b.total_days else 0):>10.2f}
 Base Amount  : ₹{self.base_amount:>10.2f}
 Tax (10 %)   : ₹{self.tax_amount:>10.2f}
 GRAND TOTAL  : ₹{self.grand_total:>10.2f}
{separator}
 Status       : {b.booking_status}
{separator}
     Thank you for staying at {hotel_name}!
         We hope to see you again soon.
{separator}
"""
        return invoice.strip()

    def save_invoice(self, directory: str = ".") -> str:
        """
        Save the invoice text to a file and return the file path.
        File name format: Invoice_<booking_id>.txt
        """
        import os
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, f"Invoice_{self.booking.booking_id:04d}.txt")
        try:
            with open(filename, "w", encoding="utf-8") as fh:
                fh.write(self.generate_invoice_text())
            return filename
        except OSError as exc:
            raise RuntimeError(f"Could not save invoice: {exc}") from exc
