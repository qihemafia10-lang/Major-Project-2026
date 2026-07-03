"""
hotel.py
--------
Business-logic layer for Room and Customer management.
The Hotel class orchestrates operations between the UI and DatabaseManager.
"""

from database import DatabaseManager
from models import Room, Customer, Booking
from utils import (Colors, log_event, validate_phone, validate_email,
                   validate_dates, calculate_days, validate_price,
                   validate_room_number, print_separator, print_table_header,
                   print_table_row, format_currency, prompt, prompt_int,
                   prompt_float, press_enter_to_continue)
from colorama import Style, Fore


class Hotel:
    """
    Central business-logic class for the Hotel Management System.
    Handles rooms, customers, bookings, and reporting.
    """

    ROOM_TYPES = ["Single", "Double", "Suite", "Deluxe", "Penthouse"]
    NAME = "Grand Horizon Hotel"

    def __init__(self, db: DatabaseManager):
        self.db = db

    # ------------------------------------------------------------------ #
    #  ROOM MANAGEMENT                                                     #
    # ------------------------------------------------------------------ #

    def view_all_rooms(self) -> None:
        """Display all rooms in a formatted table."""
        try:
            rows = self.db.get_all_rooms()
            Colors.print_header("  ALL ROOMS  ")
            if not rows:
                Colors.print_warning("No rooms found in the system.")
                press_enter_to_continue()
                return

            cols   = ["ID", "Room No", "Type", "Price/Day", "Status"]
            widths = [4, 9, 12, 12, 12]
            print_table_header(cols, widths)

            for r in rows:
                color = Fore.GREEN if r["status"] == "Available" else Fore.RED
                print_table_row(
                    [r["room_id"], r["room_number"], r["room_type"],
                     format_currency(r["price"]), r["status"]],
                    widths, color
                )
            print(f"\n  Total rooms: {len(rows)}")
        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def view_available_rooms(self) -> None:
        """Display only available rooms."""
        try:
            rows = self.db.get_available_rooms()
            Colors.print_header("  AVAILABLE ROOMS  ")
            if not rows:
                Colors.print_warning("No rooms are currently available.")
                press_enter_to_continue()
                return

            cols   = ["ID", "Room No", "Type", "Price/Day"]
            widths = [4, 9, 12, 12]
            print_table_header(cols, widths)
            for r in rows:
                print_table_row(
                    [r["room_id"], r["room_number"], r["room_type"],
                     format_currency(r["price"])],
                    widths, Fore.GREEN
                )
            print(f"\n  Available rooms: {len(rows)}")
        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def add_room(self) -> None:
        """Prompt for room details and insert into DB."""
        Colors.print_header("  ADD NEW ROOM  ")
        try:
            # Room number
            while True:
                room_number = prompt("Room Number (e.g. 101)").upper()
                if validate_room_number(room_number):
                    break
                Colors.print_error("Invalid room number. Use 1-10 alphanumeric characters.")

            # Room type
            print(f"\n  {Colors.LABEL}Room Types:{Colors.RESET}")
            for i, rt in enumerate(self.ROOM_TYPES, 1):
                print(f"    {i}. {rt}")
            choice = prompt_int("Select Room Type (1-5)", 1, 5)
            room_type = self.ROOM_TYPES[choice - 1]

            # Price
            price = prompt_float("Price per Day (₹)", min_val=0.01)

            room_id = self.db.add_room(room_number, room_type, price)
            log_event("info", f"Room added: #{room_number} [{room_type}] ₹{price:.2f} (ID:{room_id})")
            Colors.print_success(f"Room {room_number} added successfully! (ID: {room_id})")

        except ValueError as e:
            Colors.print_error(str(e))
        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def update_room(self) -> None:
        """Update an existing room's details."""
        Colors.print_header("  UPDATE ROOM  ")
        try:
            room_id = prompt_int("Enter Room ID to update", 1)
            room = self.db.get_room_by_id(room_id)
            if not room:
                Colors.print_error(f"No room found with ID {room_id}.")
                press_enter_to_continue()
                return

            Colors.print_info(f"Editing Room: {room['room_number']} | {room['room_type']} | {format_currency(room['price'])}")
            print("  (Press Enter to keep current value)\n")

            room_number = prompt("New Room Number", room["room_number"]).upper()
            if not validate_room_number(room_number):
                Colors.print_error("Invalid room number.")
                press_enter_to_continue()
                return

            print(f"\n  Room Types: {', '.join(f'{i+1}.{t}' for i,t in enumerate(self.ROOM_TYPES))}")
            type_input = prompt("New Room Type (name or leave blank)", room["room_type"])
            if type_input not in self.ROOM_TYPES:
                Colors.print_error("Invalid room type.")
                press_enter_to_continue()
                return

            price_raw = prompt("New Price per Day", str(room["price"]))
            if not validate_price(price_raw):
                Colors.print_error("Invalid price.")
                press_enter_to_continue()
                return

            self.db.update_room(room_id, room_number, type_input, float(price_raw))
            log_event("info", f"Room updated: ID={room_id} → #{room_number} [{type_input}] ₹{price_raw}")
            Colors.print_success("Room updated successfully!")

        except (ValueError, RuntimeError) as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def delete_room(self) -> None:
        """Delete a room after confirmation."""
        Colors.print_header("  DELETE ROOM  ")
        try:
            room_id = prompt_int("Enter Room ID to delete", 1)
            room = self.db.get_room_by_id(room_id)
            if not room:
                Colors.print_error(f"No room found with ID {room_id}.")
                press_enter_to_continue()
                return

            if room["status"] == "Booked":
                Colors.print_error("Cannot delete a currently booked room.")
                press_enter_to_continue()
                return

            confirm = prompt(f"Delete Room {room['room_number']}? (yes/no)", "no").lower()
            if confirm != "yes":
                Colors.print_warning("Deletion cancelled.")
                press_enter_to_continue()
                return

            self.db.delete_room(room_id)
            log_event("info", f"Room deleted: ID={room_id} #{room['room_number']}")
            Colors.print_success("Room deleted successfully!")

        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def search_rooms_by_type(self) -> None:
        """Filter and display rooms by type."""
        Colors.print_header("  SEARCH ROOMS BY TYPE  ")
        print(f"  Types: {', '.join(self.ROOM_TYPES)}")
        room_type = prompt("Enter Room Type")
        try:
            rows = self.db.get_rooms_by_type(room_type)
            if not rows:
                Colors.print_warning(f"No rooms found for type '{room_type}'.")
            else:
                cols   = ["ID", "Room No", "Type", "Price/Day", "Status"]
                widths = [4, 9, 12, 12, 12]
                print_table_header(cols, widths)
                for r in rows:
                    color = Fore.GREEN if r["status"] == "Available" else Fore.RED
                    print_table_row(
                        [r["room_id"], r["room_number"], r["room_type"],
                         format_currency(r["price"]), r["status"]],
                        widths, color
                    )
        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def filter_rooms_by_price(self) -> None:
        """Show available rooms within a max price."""
        Colors.print_header("  FILTER ROOMS BY PRICE  ")
        max_price = prompt_float("Enter Maximum Price (₹)", 0.01)
        try:
            rows = self.db.get_rooms_by_max_price(max_price)
            if not rows:
                Colors.print_warning(f"No available rooms within ₹{max_price:.2f}.")
            else:
                cols   = ["ID", "Room No", "Type", "Price/Day"]
                widths = [4, 9, 12, 12]
                print_table_header(cols, widths)
                for r in rows:
                    print_table_row(
                        [r["room_id"], r["room_number"], r["room_type"],
                         format_currency(r["price"])],
                        widths, Fore.GREEN
                    )
        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    # ------------------------------------------------------------------ #
    #  CUSTOMER MANAGEMENT                                                 #
    # ------------------------------------------------------------------ #

    def add_customer(self) -> None:
        """Collect and save a new customer record."""
        Colors.print_header("  ADD NEW CUSTOMER  ")
        try:
            name = prompt("Full Name")
            if not name:
                Colors.print_error("Name cannot be empty.")
                press_enter_to_continue()
                return

            while True:
                phone = prompt("Phone Number")
                if validate_phone(phone):
                    break
                Colors.print_error("Invalid phone. Enter 7-15 digits.")

            while True:
                email = prompt("Email Address")
                if validate_email(email):
                    break
                Colors.print_error("Invalid email format.")

            address  = prompt("Address (optional)")
            id_proof = prompt("ID Proof (Aadhar/Passport/DL - optional)")

            cid = self.db.add_customer(name, phone, email, address, id_proof)
            log_event("info", f"Customer added: {name} | {phone} (ID:{cid})")
            Colors.print_success(f"Customer '{name}' added with ID: {cid}")

        except ValueError as e:
            Colors.print_error(str(e))
        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def view_customers(self) -> None:
        """Display all customers in a table."""
        try:
            rows = self.db.get_all_customers()
            Colors.print_header("  ALL CUSTOMERS  ")
            if not rows:
                Colors.print_warning("No customers registered.")
                press_enter_to_continue()
                return

            cols   = ["ID", "Name", "Phone", "Email"]
            widths = [4, 20, 14, 26]
            print_table_header(cols, widths)
            for c in rows:
                print_table_row(
                    [c["customer_id"], c["name"], c["phone"], c["email"]],
                    widths
                )
            print(f"\n  Total customers: {len(rows)}")
        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def search_customer(self) -> None:
        """Search customers by name or phone."""
        Colors.print_header("  SEARCH CUSTOMER  ")
        keyword = prompt("Enter name or phone to search")
        try:
            rows = self.db.search_customer(keyword)
            if not rows:
                Colors.print_warning("No customers found.")
            else:
                cols   = ["ID", "Name", "Phone", "Email", "Address"]
                widths = [4, 20, 14, 24, 20]
                print_table_header(cols, widths)
                for c in rows:
                    print_table_row(
                        [c["customer_id"], c["name"], c["phone"],
                         c["email"], c["address"] or ""],
                        widths
                    )
        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def update_customer(self) -> None:
        """Update an existing customer's details."""
        Colors.print_header("  UPDATE CUSTOMER  ")
        try:
            cid = prompt_int("Enter Customer ID to update", 1)
            c   = self.db.get_customer_by_id(cid)
            if not c:
                Colors.print_error(f"No customer found with ID {cid}.")
                press_enter_to_continue()
                return

            Colors.print_info(f"Editing: {c['name']} | {c['phone']}")
            print("  (Press Enter to keep current value)\n")

            name = prompt("Full Name", c["name"])

            while True:
                phone = prompt("Phone", c["phone"])
                if validate_phone(phone):
                    break
                Colors.print_error("Invalid phone.")

            while True:
                email = prompt("Email", c["email"])
                if validate_email(email):
                    break
                Colors.print_error("Invalid email.")

            address  = prompt("Address",  c["address"]  or "")
            id_proof = prompt("ID Proof", c["id_proof"] or "")

            self.db.update_customer(cid, name, phone, email, address, id_proof)
            log_event("info", f"Customer updated: ID={cid} {name}")
            Colors.print_success("Customer updated successfully!")

        except (ValueError, RuntimeError) as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def delete_customer(self) -> None:
        """Delete a customer after confirmation."""
        Colors.print_header("  DELETE CUSTOMER  ")
        try:
            cid = prompt_int("Enter Customer ID to delete", 1)
            c   = self.db.get_customer_by_id(cid)
            if not c:
                Colors.print_error(f"No customer found with ID {cid}.")
                press_enter_to_continue()
                return

            confirm = prompt(f"Delete customer '{c['name']}'? (yes/no)", "no").lower()
            if confirm != "yes":
                Colors.print_warning("Deletion cancelled.")
                press_enter_to_continue()
                return

            self.db.delete_customer(cid)
            log_event("info", f"Customer deleted: ID={cid} {c['name']}")
            Colors.print_success("Customer deleted successfully!")

        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    # ------------------------------------------------------------------ #
    #  BOOKING                                                             #
    # ------------------------------------------------------------------ #

    def book_room(self) -> None:
        """Walk through the full booking flow."""
        Colors.print_header("  BOOK A ROOM  ")
        try:
            # 1. Select customer
            cid = prompt_int("Enter Customer ID", 1)
            customer = self.db.get_customer_by_id(cid)
            if not customer:
                Colors.print_error(f"No customer found with ID {cid}.")
                press_enter_to_continue()
                return
            Colors.print_info(f"Customer: {customer['name']} | {customer['phone']}")

            # 2. Show and select available room
            available = self.db.get_available_rooms()
            if not available:
                Colors.print_error("No rooms are currently available.")
                press_enter_to_continue()
                return

            cols   = ["ID", "Room No", "Type", "Price/Day"]
            widths = [4, 9, 12, 12]
            print()
            print_table_header(cols, widths)
            for r in available:
                print_table_row(
                    [r["room_id"], r["room_number"], r["room_type"],
                     format_currency(r["price"])],
                    widths, Fore.GREEN
                )

            room_id = prompt_int("\n  Enter Room ID to book", 1)
            room    = self.db.get_room_by_id(room_id)
            if not room:
                Colors.print_error("Invalid Room ID.")
                press_enter_to_continue()
                return
            if room["status"] != "Available":
                Colors.print_error(f"Room {room['room_number']} is already booked.")
                press_enter_to_continue()
                return

            # 3. Dates
            check_in  = prompt("Check-In  Date (YYYY-MM-DD)")
            check_out = prompt("Check-Out Date (YYYY-MM-DD)")
            valid, reason = validate_dates(check_in, check_out)
            if not valid:
                Colors.print_error(reason)
                press_enter_to_continue()
                return

            total_days  = calculate_days(check_in, check_out)
            bill_amount = round(room["price"] * total_days, 2)

            # 4. Summary
            print_separator()
            Colors.print_info(f"  Customer   : {customer['name']}")
            Colors.print_info(f"  Room       : {room['room_number']} ({room['room_type']})")
            Colors.print_info(f"  Check-In   : {check_in}")
            Colors.print_info(f"  Check-Out  : {check_out}")
            Colors.print_info(f"  Total Days : {total_days}")
            Colors.print_info(f"  Base Bill  : {format_currency(bill_amount)}")
            print_separator()

            confirm = prompt("Confirm booking? (yes/no)", "no").lower()
            if confirm != "yes":
                Colors.print_warning("Booking cancelled.")
                press_enter_to_continue()
                return

            booking_id = self.db.create_booking(cid, room_id, check_in, check_out,
                                                 total_days, bill_amount)
            self.db.update_room_status(room_id, "Booked")

            log_event("info",
                      f"Booking created: ID={booking_id} | Customer={customer['name']} "
                      f"| Room={room['room_number']} | {check_in} to {check_out} "
                      f"| ₹{bill_amount:.2f}")
            Colors.print_success(f"Room booked successfully! Booking ID: {booking_id}")

        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def check_in(self) -> None:
        """Display booking details for check-in."""
        Colors.print_header("  CHECK-IN  ")
        try:
            bid     = prompt_int("Enter Booking ID", 1)
            booking = self.db.get_booking_by_id(bid)
            if not booking:
                Colors.print_error(f"No booking found with ID {bid}.")
                press_enter_to_continue()
                return

            if booking["booking_status"] != "Confirmed":
                Colors.print_warning(f"Booking status is '{booking['booking_status']}'. Cannot check in.")
                press_enter_to_continue()
                return

            print_separator()
            print(f"  {Colors.LABEL}Booking ID    :{Colors.RESET} {booking['booking_id']}")
            print(f"  {Colors.LABEL}Customer      :{Colors.RESET} {booking['customer_name']}")
            print(f"  {Colors.LABEL}Room          :{Colors.RESET} {booking['room_number']} ({booking['room_type']})")
            print(f"  {Colors.LABEL}Check-In      :{Colors.RESET} {booking['check_in']}")
            print(f"  {Colors.LABEL}Check-Out     :{Colors.RESET} {booking['check_out']}")
            print(f"  {Colors.LABEL}Total Days    :{Colors.RESET} {booking['total_days']}")
            print(f"  {Colors.LABEL}Base Amount   :{Colors.RESET} {format_currency(booking['bill_amount'])}")
            print_separator()

            self.db.update_booking_status(bid, "Checked-In")
            log_event("info", f"Check-In: Booking ID={bid} | {booking['customer_name']}")
            Colors.print_success("Check-In successful! Welcome to the hotel.")

        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def check_out(self) -> None:
        """Process check-out and generate invoice."""
        Colors.print_header("  CHECK-OUT  ")
        try:
            bid     = prompt_int("Enter Booking ID", 1)
            booking = self.db.get_booking_by_id(bid)
            if not booking:
                Colors.print_error(f"No booking found with ID {bid}.")
                press_enter_to_continue()
                return

            if booking["booking_status"] not in ("Confirmed", "Checked-In"):
                Colors.print_warning(f"Booking status is '{booking['booking_status']}'. Already checked out.")
                press_enter_to_continue()
                return

            self.db.update_booking_status(bid, "Completed")
            self.db.update_room_status(booking["room_id"], "Available")

            log_event("info",
                      f"Check-Out: Booking ID={bid} | {booking['customer_name']} "
                      f"| Room={booking['room_number']} | ₹{booking['bill_amount']:.2f}")
            Colors.print_success("Check-Out complete. Room is now available.")

        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def view_booking_history(self) -> None:
        """Show all bookings (history)."""
        Colors.print_header("  BOOKING HISTORY  ")
        try:
            rows = self.db.get_all_bookings()
            if not rows:
                Colors.print_warning("No bookings found.")
                press_enter_to_continue()
                return

            cols   = ["BID", "Customer", "Room", "Check-In", "Check-Out", "Amount", "Status"]
            widths = [4, 18, 7, 12, 12, 12, 12]
            print_table_header(cols, widths)
            for b in rows:
                status = b["booking_status"]
                color  = (Fore.GREEN  if status == "Completed"  else
                          Fore.CYAN   if status == "Checked-In" else
                          Fore.YELLOW if status == "Confirmed"  else Fore.WHITE)
                print_table_row(
                    [b["booking_id"], b["customer_name"], b["room_number"],
                     b["check_in"], b["check_out"],
                     format_currency(b["bill_amount"]), status],
                    widths, color
                )
        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    # ------------------------------------------------------------------ #
    #  REPORTS                                                             #
    # ------------------------------------------------------------------ #

    def daily_revenue_report(self) -> None:
        """Show revenue for a specific date."""
        Colors.print_header("  DAILY REVENUE REPORT  ")
        date_str = prompt("Enter date (YYYY-MM-DD)")
        from utils import validate_date
        if not validate_date(date_str):
            Colors.print_error("Invalid date format.")
            press_enter_to_continue()
            return
        try:
            rev = self.db.get_daily_revenue(date_str)
            Colors.print_info(f"Revenue on {date_str}: {format_currency(rev)}")
        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def monthly_revenue_report(self) -> None:
        """Show revenue for a given month."""
        Colors.print_header("  MONTHLY REVENUE REPORT  ")
        year  = prompt_int("Enter Year  (e.g. 2025)", 2000, 2100)
        month = prompt_int("Enter Month (1-12)", 1, 12)
        try:
            rev = self.db.get_monthly_revenue(year, month)
            Colors.print_info(f"Revenue for {year}-{month:02d}: {format_currency(rev)}")
        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()

    def show_dashboard(self) -> None:
        """Print a summary statistics dashboard."""
        Colors.print_header("  DASHBOARD STATISTICS  ")
        try:
            s = self.db.get_dashboard_stats()
            print_separator("─", 40)
            print(f"  {Colors.LABEL}Total Rooms      :{Colors.RESET} {s['total_rooms']}")
            print(f"  {Colors.GREEN}Available Rooms  :{Colors.RESET} {s['available_rooms']}")
            print(f"  {Colors.RED}Booked Rooms     :{Colors.RESET} {s['booked_rooms']}")
            print_separator("─", 40)
            print(f"  {Colors.LABEL}Total Customers  :{Colors.RESET} {s['total_customers']}")
            print(f"  {Colors.LABEL}Total Bookings   :{Colors.RESET} {s['total_bookings']}")
            print(f"  {Colors.CYAN}Active Bookings  :{Colors.RESET} {s['active_bookings']}")
            print_separator("─", 40)
            print(f"  {Colors.SUCCESS}Total Revenue    :{Colors.RESET} {format_currency(s['total_revenue'])}")
            print_separator("─", 40)
        except RuntimeError as e:
            Colors.print_error(str(e))
        press_enter_to_continue()
