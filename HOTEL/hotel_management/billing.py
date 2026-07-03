"""
billing.py
----------
Billing controller: generates and saves invoices.
Wraps the Billing model to provide a CLI-driven interface.
"""

import os
from database import DatabaseManager
from models import Booking, Billing
from utils import (Colors, log_event, prompt_int,
                   press_enter_to_continue, print_separator)


INVOICE_DIR = os.path.join(os.path.dirname(__file__), "..", "invoices")


class BillingManager:
    """
    Handles invoice generation and display.
    Delegates calculation to the Billing model class.
    """

    def __init__(self, db: DatabaseManager, hotel_name: str = "Grand Horizon Hotel"):
        self.db         = db
        self.hotel_name = hotel_name

    def generate_invoice(self) -> None:
        """Prompt for a booking ID, print the invoice, and save it to a file."""
        Colors.print_header("  GENERATE INVOICE  ")
        try:
            bid     = prompt_int("Enter Booking ID", 1)
            row     = self.db.get_booking_by_id(bid)
            if not row:
                Colors.print_error(f"No booking found with ID {bid}.")
                press_enter_to_continue()
                return

            booking = Booking.from_row(row)
            billing = Billing(booking)
            invoice_text = billing.generate_invoice_text(self.hotel_name)

            # ---- Print to terminal ----
            print()
            for line in invoice_text.splitlines():
                print(f"  {Colors.CYAN}{line}{Colors.RESET}")

            # ---- Save to file ----
            filepath = billing.save_invoice(INVOICE_DIR)
            log_event("info", f"Invoice generated: Booking ID={bid} | saved to {filepath}")
            Colors.print_success(f"Invoice saved → {filepath}")

        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()
