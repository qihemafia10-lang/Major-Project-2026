"""
main.py
-------
Entry point for the Hotel Management System.
Handles admin login, the main menu loop, and dispatches to subsystems.
"""

import sys
from colorama import Fore, Style

from database import DatabaseManager
from hotel import Hotel
from billing import BillingManager
from utils import (Colors, log_event, clear_screen,
                   press_enter_to_continue, get_password_input, prompt)


HOTEL_NAME = "Grand Horizon Hotel"


# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------

def print_banner() -> None:
    """Display the application banner."""
    clear_screen()
    banner = f"""
{Colors.HEADER}
  ╔══════════════════════════════════════════════════════╗
  ║                                                      ║
  ║         🏨  HOTEL MANAGEMENT SYSTEM  🏨              ║
  ║              {HOTEL_NAME:<38}║
  ║                                                      ║
  ╚══════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(banner)


# ---------------------------------------------------------------------------
# Admin Login
# ---------------------------------------------------------------------------

def admin_login(db: DatabaseManager) -> bool:
    """
    Prompt for credentials and return True if valid.
    Allows up to 3 attempts.
    """
    Colors.print_header("  ADMIN LOGIN  ")
    for attempt in range(1, 4):
        try:
            username = prompt("Username")
            password = get_password_input("  Password: ")
            if db.verify_admin(username, password):
                log_event("info", f"Admin login successful: '{username}'")
                Colors.print_success(f"Welcome, {username}! Login successful.")
                return True
            Colors.print_error(f"Invalid credentials. Attempt {attempt}/3.")
        except KeyboardInterrupt:
            print()
            Colors.print_warning("Login interrupted.")
            return False
    log_event("warning", "Admin login failed: 3 incorrect attempts.")
    Colors.print_error("Too many failed attempts. Exiting.")
    return False


# ---------------------------------------------------------------------------
# Menu display
# ---------------------------------------------------------------------------

def print_menu() -> None:
    """Print the main navigation menu."""
    M = Colors.MENU
    L = Colors.LABEL
    R = Colors.RESET
    D = Colors.DIM

    print(f"\n{M}  ╔══════════════════════════════════╗")
    print(f"  ║      MAIN MENU                   ║")
    print(f"  ╠══════════════════════════════════╣{R}")
    print(f"  {L}  ── Room Management ──{R}")
    print(f"   {D}1.{R}  View All Rooms")
    print(f"   {D}2.{R}  View Available Rooms")
    print(f"   {D}3.{R}  Add Room")
    print(f"   {D}4.{R}  Update Room")
    print(f"   {D}5.{R}  Delete Room")
    print(f"   {D}6.{R}  Search Room by Type")
    print(f"   {D}7.{R}  Filter Rooms by Price")
    print(f"  {L}  ── Customer Management ──{R}")
    print(f"   {D}8.{R}  Add Customer")
    print(f"   {D}9.{R}  View Customers")
    print(f"  {D}10.{R}  Search Customer")
    print(f"  {D}11.{R}  Update Customer")
    print(f"  {D}12.{R}  Delete Customer")
    print(f"  {L}  ── Reservations ──{R}")
    print(f"  {D}13.{R}  Book Room")
    print(f"  {D}14.{R}  Check In")
    print(f"  {D}15.{R}  Check Out")
    print(f"  {D}16.{R}  Booking History")
    print(f"  {L}  ── Billing & Reports ──{R}")
    print(f"  {D}17.{R}  Generate Invoice")
    print(f"  {D}18.{R}  Daily Revenue Report")
    print(f"  {D}19.{R}  Monthly Revenue Report")
    print(f"  {D}20.{R}  Dashboard Statistics")
    print(f"  {L}  ── System ──{R}")
    print(f"  {D}21.{R}  {Fore.RED}Exit{R}")
    print(f"{M}  ╚══════════════════════════════════╝{R}")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Application entry point.
    Initialises subsystems, authenticates the admin, then runs the menu loop.
    """
    print_banner()

    # Initialise database and subsystems
    try:
        db      = DatabaseManager()
        hotel   = Hotel(db)
        billing = BillingManager(db, HOTEL_NAME)
    except RuntimeError as exc:
        Colors.print_error(f"Startup error: {exc}")
        sys.exit(1)

    # Admin login
    if not admin_login(db):
        sys.exit(0)

    # Dispatch table: menu choice → callable
    actions = {
        1:  hotel.view_all_rooms,
        2:  hotel.view_available_rooms,
        3:  hotel.add_room,
        4:  hotel.update_room,
        5:  hotel.delete_room,
        6:  hotel.search_rooms_by_type,
        7:  hotel.filter_rooms_by_price,
        8:  hotel.add_customer,
        9:  hotel.view_customers,
        10: hotel.search_customer,
        11: hotel.update_customer,
        12: hotel.delete_customer,
        13: hotel.book_room,
        14: hotel.check_in,
        15: hotel.check_out,
        16: hotel.view_booking_history,
        17: billing.generate_invoice,
        18: hotel.daily_revenue_report,
        19: hotel.monthly_revenue_report,
        20: hotel.show_dashboard,
    }

    log_event("info", "Hotel Management System started.")

    while True:
        try:
            print_banner()
            print_menu()
            raw = input(f"\n{Colors.LABEL}  Enter choice (1-21): {Colors.RESET}").strip()

            if not raw:
                continue

            choice = int(raw)

            if choice == 21:
                log_event("info", "Hotel Management System exited normally.")
                Colors.print_success("Thank you! Goodbye.")
                break

            action = actions.get(choice)
            if action:
                action()
            else:
                Colors.print_error("Invalid choice. Please enter a number between 1 and 21.")
                press_enter_to_continue()

        except ValueError:
            Colors.print_error("Invalid input. Please enter a numeric menu choice.")
            press_enter_to_continue()

        except KeyboardInterrupt:
            print()
            Colors.print_warning("\nInterrupted. Type 21 to exit gracefully.")
            press_enter_to_continue()

        except Exception as exc:  # Broad catch for unexpected runtime errors
            Colors.print_error(f"Unexpected error: {exc}")
            log_event("error", f"Unexpected error in main loop: {exc}")
            press_enter_to_continue()


if __name__ == "__main__":
    main()
