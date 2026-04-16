"""
Smart Campus Facility Management System (SCFMS)
================================================
Object-Oriented Design Implementation - Group 24
Sasi Sai Nadh Boddu | GWID: G22742105

Based on the UML diagrams:
- Use Case Model: Student actor, Notification Service actor
- Domain Model: Student, Booking, Room, CheckIn, MaintenanceTicket, etc.
- Class Diagram: Boundary/Control/Entity pattern (BCE)
- Activity Diagrams: Authentication, Search Availability, Book Room,
                     Check-In, Maintenance Ticket, Track Ticket Status

Language: Python (originally designed for Java)
"""

import datetime
import hashlib
import uuid
from typing import Optional


# ============================================================
# ENTITY CLASSES (from Domain Model & Class Diagram)
# ============================================================

class Student:
    """Entity: Represents a campus student user."""

    def __init__(self, student_id: int, name: str, email: str):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.credential: Optional[Credential] = None
        self.bookings: list["Booking"] = []
        self.maintenance_tickets: list["MaintenanceTicket"] = []

    def __repr__(self):
        return f"Student(id={self.student_id}, name='{self.name}', email='{self.email}')"


class Credential:
    """Entity: Authentication credentials for a student."""

    def __init__(self, username: str, password: str):
        self.username = username
        # Store hashed password for security
        self.password_hash = self._hash_password(password)

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify(self, username: str, password: str) -> bool:
        return (self.username == username and
                self.password_hash == self._hash_password(password))

    def __repr__(self):
        return f"Credential(username='{self.username}')"


class Room:
    """Entity: Represents a campus room."""

    def __init__(self, room_id: int, room_number: str, capacity: int, building: str):
        self.room_id = room_id
        self.room_number = room_number
        self.capacity = capacity
        self.building = building
        self.status = "Available"  # Available, Occupied, Under Maintenance
        self.availability_calendar = AvailabilityCalendar(room_id)

    def __repr__(self):
        return (f"Room(id={self.room_id}, number='{self.room_number}', "
                f"building='{self.building}', capacity={self.capacity}, status='{self.status}')")


class AvailabilityCalendar:
    """Entity: Tracks room availability by date and time slots."""

    def __init__(self, calendar_id: int):
        self.calendar_id = calendar_id
        # slot_key = (date_str, start_time, end_time) -> booked (True/False)
        self.slots: dict[tuple, bool] = {}

    def is_available(self, date_str: str, start_time: str, end_time: str) -> bool:
        key = (date_str, start_time, end_time)
        return not self.slots.get(key, False)

    def reserve_slot(self, date_str: str, start_time: str, end_time: str):
        key = (date_str, start_time, end_time)
        self.slots[key] = True

    def release_slot(self, date_str: str, start_time: str, end_time: str):
        key = (date_str, start_time, end_time)
        self.slots[key] = False


class BookingStatus:
    """Entity: Status of a booking."""
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    CHECKED_IN = "Checked-In"
    COMPLETED = "Completed"
    PENDING = "Pending"


class Booking:
    """Entity: Represents a room booking made by a student."""

    def __init__(self, booking_id: int, student: Student, room: Room,
                 booking_date: str, start_time: str, end_time: str):
        self.booking_id = booking_id
        self.student = student
        self.room = room
        self.booking_date = booking_date
        self.start_time = start_time
        self.end_time = end_time
        self.status = BookingStatus.CONFIRMED
        self.check_in: Optional[CheckInLog] = None

    def __repr__(self):
        return (f"Booking(id={self.booking_id}, room='{self.room.room_number}', "
                f"date='{self.booking_date}', time='{self.start_time}-{self.end_time}', "
                f"status='{self.status}')")


class CheckInLog:
    """Entity: Records when a student checks into a booked room."""

    def __init__(self, check_in_log_id: int, booking: Booking):
        self.check_in_log_id = check_in_log_id
        self.booking = booking
        self.check_in_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return f"CheckInLog(id={self.check_in_log_id}, time='{self.check_in_time}')"


class TicketStatus:
    """Entity: Status values for maintenance tickets."""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class StatusHistory:
    """Entity: Tracks status changes for a maintenance ticket."""

    def __init__(self, history_id: int, status: str):
        self.history_id = history_id
        self.status = status
        self.updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return f"StatusHistory(status='{self.status}', updated_at='{self.updated_at}')"


class MaintenanceTicket:
    """Entity: Represents a maintenance request submitted by a student."""

    def __init__(self, ticket_id: int, student: Student, room: Room, description: str):
        self.ticket_id = ticket_id
        self.student = student
        self.room = room
        self.description = description
        self.current_status = TicketStatus.OPEN
        self.status_history: list[StatusHistory] = [
            StatusHistory(1, TicketStatus.OPEN)
        ]

    def update_status(self, new_status: str):
        self.current_status = new_status
        history_id = len(self.status_history) + 1
        self.status_history.append(StatusHistory(history_id, new_status))

    def __repr__(self):
        return (f"MaintenanceTicket(id={self.ticket_id}, room='{self.room.room_number}', "
                f"status='{self.current_status}')")


class NotificationService:
    """Entity: External actor that sends notifications."""

    @staticmethod
    def send_notification(student: Student, message: str):
        print(f"  [NOTIFICATION -> {student.name} ({student.email})]: {message}")


# ============================================================
# CONTROLLER CLASSES (from Class Diagram - «control» stereotype)
# ============================================================

class AuthController:
    """Control: Handles authentication logic."""

    def __init__(self, students: list[Student]):
        self.students = {s.credential.username: s for s in students if s.credential}

    def authenticate(self, username: str, password: str) -> Optional[Student]:
        student = self.students.get(username)
        if student and student.credential.verify(username, password):
            return student
        return None


class RoomSearchController:
    """Control: Handles room search and availability checking."""

    def __init__(self, rooms: list[Room]):
        self.rooms = rooms

    def search_available_rooms(self, date_str: str, start_time: str,
                                end_time: str, min_capacity: int = 0) -> list[Room]:
        available = []
        for room in self.rooms:
            if room.status == "Under Maintenance":
                continue
            if room.capacity >= min_capacity:
                if room.availability_calendar.is_available(date_str, start_time, end_time):
                    available.append(room)
        return available


class RoomBookingController:
    """Control: Handles room booking logic."""

    _booking_counter = 0

    def __init__(self, rooms: list[Room]):
        self.rooms = {r.room_id: r for r in rooms}
        self.bookings: dict[int, Booking] = {}

    def book_room(self, student: Student, room_id: int, date_str: str,
                  start_time: str, end_time: str) -> Optional[Booking]:
        room = self.rooms.get(room_id)
        if not room:
            return None

        # Check availability
        if not room.availability_calendar.is_available(date_str, start_time, end_time):
            return None

        # Reserve the slot
        room.availability_calendar.reserve_slot(date_str, start_time, end_time)

        # Create booking
        RoomBookingController._booking_counter += 1
        booking = Booking(
            booking_id=RoomBookingController._booking_counter,
            student=student,
            room=room,
            booking_date=date_str,
            start_time=start_time,
            end_time=end_time
        )
        self.bookings[booking.booking_id] = booking
        student.bookings.append(booking)

        # Notify
        NotificationService.send_notification(
            student,
            f"Booking confirmed! Room {room.room_number} on {date_str} "
            f"from {start_time} to {end_time}. Booking ID: {booking.booking_id}"
        )
        return booking

    def cancel_booking(self, booking_id: int) -> bool:
        booking = self.bookings.get(booking_id)
        if not booking or booking.status == BookingStatus.CANCELLED:
            return False

        booking.status = BookingStatus.CANCELLED
        booking.room.availability_calendar.release_slot(
            booking.booking_date, booking.start_time, booking.end_time
        )
        NotificationService.send_notification(
            booking.student,
            f"Booking {booking_id} for Room {booking.room.room_number} has been cancelled."
        )
        return True


class CheckInController:
    """Control: Handles the check-in process for booked rooms."""

    _checkin_counter = 0

    def check_in(self, booking_id: int, booking_controller: RoomBookingController) -> Optional[CheckInLog]:
        booking = booking_controller.bookings.get(booking_id)
        if not booking:
            return None
        if booking.status != BookingStatus.CONFIRMED:
            return None

        CheckInController._checkin_counter += 1
        check_in_log = CheckInLog(
            check_in_log_id=CheckInController._checkin_counter,
            booking=booking
        )
        booking.check_in = check_in_log
        booking.status = BookingStatus.CHECKED_IN
        booking.room.status = "Occupied"

        NotificationService.send_notification(
            booking.student,
            f"Checked in to Room {booking.room.room_number}. Enjoy your session!"
        )
        return check_in_log


class MaintenanceTicketController:
    """Control: Handles maintenance ticket creation and management."""

    _ticket_counter = 0

    def __init__(self):
        self.tickets: dict[int, MaintenanceTicket] = {}

    def create_ticket(self, student: Student, room: Room, description: str) -> MaintenanceTicket:
        MaintenanceTicketController._ticket_counter += 1
        ticket = MaintenanceTicket(
            ticket_id=MaintenanceTicketController._ticket_counter,
            student=student,
            room=room,
            description=description
        )
        self.tickets[ticket.ticket_id] = ticket
        student.maintenance_tickets.append(ticket)

        NotificationService.send_notification(
            student,
            f"Maintenance ticket #{ticket.ticket_id} submitted for "
            f"Room {room.room_number}: '{description}'"
        )
        return ticket

    def update_ticket_status(self, ticket_id: int, new_status: str) -> bool:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False
        ticket.update_status(new_status)
        NotificationService.send_notification(
            ticket.student,
            f"Ticket #{ticket_id} status updated to: {new_status}"
        )
        return True


class TicketStatusController:
    """Control: Retrieves ticket status information."""

    def __init__(self, ticket_controller: MaintenanceTicketController):
        self.ticket_controller = ticket_controller

    def get_status(self, ticket_id: int) -> Optional[MaintenanceTicket]:
        return self.ticket_controller.tickets.get(ticket_id)

    def get_student_tickets(self, student: Student) -> list[MaintenanceTicket]:
        return student.maintenance_tickets


# ============================================================
# BOUNDARY CLASSES (from Class Diagram - «boundary» stereotype)
# These simulate the UI layer with console I/O
# ============================================================

class LoginUI:
    """Boundary: Login interface."""

    def __init__(self, auth_controller: AuthController):
        self.auth_controller = auth_controller

    def show(self) -> Optional[Student]:
        print("\n" + "=" * 60)
        print("  SCFMS - Smart Campus Facility Management System")
        print("  Login")
        print("=" * 60)
        username = input("  Username: ").strip()
        password = input("  Password: ").strip()

        student = self.auth_controller.authenticate(username, password)
        if student:
            print(f"\n  ✓ Welcome, {student.name}!")
            return student
        else:
            print("\n  ✗ Invalid credentials. Please try again.")
            return None


class SearchAvailabilityUI:
    """Boundary: Room search interface."""

    def __init__(self, search_controller: RoomSearchController):
        self.search_controller = search_controller

    def enter_criteria(self) -> tuple:
        print("\n" + "-" * 50)
        print("  Search Available Rooms")
        print("-" * 50)
        date_str = input("  Date (YYYY-MM-DD): ").strip()
        start_time = input("  Start Time (HH:MM): ").strip()
        end_time = input("  End Time (HH:MM): ").strip()
        min_cap_str = input("  Minimum Capacity (or press Enter for any): ").strip()
        min_capacity = int(min_cap_str) if min_cap_str else 0
        return date_str, start_time, end_time, min_capacity

    def show_available_rooms(self, date_str: str, start_time: str,
                              end_time: str, min_capacity: int = 0) -> list[Room]:
        print("\n  Searching...")
        rooms = self.search_controller.search_available_rooms(
            date_str, start_time, end_time, min_capacity
        )
        if rooms:
            print(f"\n  Found {len(rooms)} available room(s):\n")
            print(f"  {'ID':<6}{'Room':<12}{'Building':<18}{'Capacity':<10}{'Status'}")
            print(f"  {'-'*6}{'-'*12}{'-'*18}{'-'*10}{'-'*12}")
            for room in rooms:
                print(f"  {room.room_id:<6}{room.room_number:<12}"
                      f"{room.building:<18}{room.capacity:<10}{room.status}")
        else:
            print("\n  No rooms available for the given criteria.")
        return rooms


class RoomBookingUI:
    """Boundary: Room booking interface."""

    def __init__(self, booking_controller: RoomBookingController):
        self.booking_controller = booking_controller

    def start_booking(self, student: Student, available_rooms: list[Room],
                      date_str: str, start_time: str, end_time: str) -> Optional[Booking]:
        if not available_rooms:
            print("\n  No rooms available to book.")
            return None

        print("\n" + "-" * 50)
        print("  Book a Room")
        print("-" * 50)
        room_id_str = input("  Enter Room ID to book: ").strip()
        try:
            room_id = int(room_id_str)
        except ValueError:
            print("  ✗ Invalid Room ID.")
            return None

        booking = self.booking_controller.book_room(
            student, room_id, date_str, start_time, end_time
        )
        if booking:
            print(f"\n  ✓ Booking confirmed!")
            self.show_confirmation(booking)
            return booking
        else:
            print("\n  ✗ Booking failed. Room may no longer be available.")
            return None

    def show_confirmation(self, booking: Booking):
        print(f"    Booking ID:  {booking.booking_id}")
        print(f"    Room:        {booking.room.room_number} ({booking.room.building})")
        print(f"    Date:        {booking.booking_date}")
        print(f"    Time:        {booking.start_time} - {booking.end_time}")
        print(f"    Status:      {booking.status}")


class CheckInUI:
    """Boundary: Check-in interface."""

    def __init__(self, checkin_controller: CheckInController,
                 booking_controller: RoomBookingController):
        self.checkin_controller = checkin_controller
        self.booking_controller = booking_controller

    def request_check_in(self, student: Student) -> Optional[CheckInLog]:
        print("\n" + "-" * 50)
        print("  Room Check-In")
        print("-" * 50)

        # Show student's confirmed bookings
        confirmed = [b for b in student.bookings if b.status == BookingStatus.CONFIRMED]
        if not confirmed:
            print("  No confirmed bookings to check in.")
            return None

        print("  Your confirmed bookings:\n")
        for b in confirmed:
            print(f"    [{b.booking_id}] Room {b.room.room_number} on "
                  f"{b.booking_date} ({b.start_time}-{b.end_time})")

        booking_id_str = input("\n  Enter Booking ID to check in: ").strip()
        try:
            booking_id = int(booking_id_str)
        except ValueError:
            print("  ✗ Invalid Booking ID.")
            return None

        check_in_log = self.checkin_controller.check_in(booking_id, self.booking_controller)
        if check_in_log:
            self.show_check_in_confirmation(check_in_log)
            return check_in_log
        else:
            print("  ✗ Check-in failed. Booking may not exist or is not confirmed.")
            return None

    def show_check_in_confirmation(self, log: CheckInLog):
        print(f"\n  ✓ Checked in successfully!")
        print(f"    Check-In ID: {log.check_in_log_id}")
        print(f"    Room:        {log.booking.room.room_number}")
        print(f"    Time:        {log.check_in_time}")


class MaintenanceTicketUI:
    """Boundary: Maintenance ticket submission interface."""

    def __init__(self, ticket_controller: MaintenanceTicketController, rooms: list[Room]):
        self.ticket_controller = ticket_controller
        self.rooms = {r.room_id: r for r in rooms}

    def submit_issue(self, student: Student) -> Optional[MaintenanceTicket]:
        print("\n" + "-" * 50)
        print("  Submit Maintenance Ticket")
        print("-" * 50)

        room_id_str = input("  Room ID with the issue: ").strip()
        try:
            room_id = int(room_id_str)
        except ValueError:
            print("  ✗ Invalid Room ID.")
            return None

        room = self.rooms.get(room_id)
        if not room:
            print("  ✗ Room not found.")
            return None

        description = input("  Describe the issue: ").strip()
        if not description:
            print("  ✗ Description cannot be empty.")
            return None

        ticket = self.ticket_controller.create_ticket(student, room, description)
        self.show_ticket_submitted(ticket)
        return ticket

    def show_ticket_submitted(self, ticket: MaintenanceTicket):
        print(f"\n  ✓ Ticket submitted successfully!")
        print(f"    Ticket ID:   {ticket.ticket_id}")
        print(f"    Room:        {ticket.room.room_number}")
        print(f"    Description: {ticket.description}")
        print(f"    Status:      {ticket.current_status}")


class TicketStatusUI:
    """Boundary: Ticket status tracking interface."""

    def __init__(self, status_controller: TicketStatusController):
        self.status_controller = status_controller

    def enter_ticket_id(self, student: Student):
        print("\n" + "-" * 50)
        print("  Track Maintenance Ticket Status")
        print("-" * 50)

        tickets = self.status_controller.get_student_tickets(student)
        if not tickets:
            print("  No maintenance tickets found.")
            return

        print("  Your tickets:\n")
        for t in tickets:
            print(f"    [{t.ticket_id}] Room {t.room.room_number} - "
                  f"Status: {t.current_status}")

        ticket_id_str = input("\n  Enter Ticket ID for details (or press Enter to skip): ").strip()
        if not ticket_id_str:
            return

        try:
            ticket_id = int(ticket_id_str)
        except ValueError:
            print("  ✗ Invalid Ticket ID.")
            return

        ticket = self.status_controller.get_status(ticket_id)
        if ticket:
            self.show_status(ticket)
        else:
            print("  ✗ Ticket not found.")

    def show_status(self, ticket: MaintenanceTicket):
        print(f"\n  Ticket #{ticket.ticket_id} Details:")
        print(f"    Room:        {ticket.room.room_number}")
        print(f"    Description: {ticket.description}")
        print(f"    Current:     {ticket.current_status}")
        print(f"\n    Status History:")
        for h in ticket.status_history:
            print(f"      [{h.updated_at}] {h.status}")


# ============================================================
# MAIN APPLICATION
# ============================================================

class SCFMSApplication:
    """Main application controller - orchestrates the system."""

    def __init__(self):
        # Initialize sample data
        self.students = self._create_sample_students()
        self.rooms = self._create_sample_rooms()

        # Initialize controllers
        self.auth_controller = AuthController(self.students)
        self.search_controller = RoomSearchController(self.rooms)
        self.booking_controller = RoomBookingController(self.rooms)
        self.checkin_controller = CheckInController()
        self.ticket_controller = MaintenanceTicketController()
        self.status_controller = TicketStatusController(self.ticket_controller)

        # Initialize UIs (boundaries)
        self.login_ui = LoginUI(self.auth_controller)
        self.search_ui = SearchAvailabilityUI(self.search_controller)
        self.booking_ui = RoomBookingUI(self.booking_controller)
        self.checkin_ui = CheckInUI(self.checkin_controller, self.booking_controller)
        self.ticket_ui = MaintenanceTicketUI(self.ticket_controller, self.rooms)
        self.ticket_status_ui = TicketStatusUI(self.status_controller)

    def _create_sample_students(self) -> list[Student]:
        students = []

        s1 = Student(1, "Sasi Sai Nadh Boddu", "sasi@gwu.edu")
        s1.credential = Credential("sasi", "password123")
        students.append(s1)

        s2 = Student(2, "Nikhil", "nik@gwu.edu")
        s2.credential = Credential("nikhil", "pass456")
        students.append(s2)

        s3 = Student(3, "Alice", "alice@gwu.edu")
        s3.credential = Credential("alice", "alice789")
        students.append(s3)

        return students

    def _create_sample_rooms(self) -> list[Room]:
        return [
            Room(101, "B101", 30, "Science Building"),
            Room(102, "B102", 50, "Science Building"),
            Room(201, "L201", 20, "Library"),
            Room(202, "L202", 40, "Library"),
            Room(301, "E301", 60, "Engineering Hall"),
            Room(302, "E302", 25, "Engineering Hall"),
            Room(401, "A401", 100, "Auditorium"),
            Room(501, "C501", 15, "Computer Lab"),
        ]

    def run(self):
        print("\n" + "=" * 60)
        print("  ╔═══════════════════════════════════════════════╗")
        print("  ║   SCFMS - Smart Campus Facility Management   ║")
        print("  ║   Intelligent Solutions for Campus Ops        ║")
        print("  ║   Group 24 | Sasi Sai Nadh Boddu             ║")
        print("  ╚═══════════════════════════════════════════════╝")
        print("=" * 60)
        print("\n  Sample credentials:")
        print("    sasi / password123")
        print("    john / pass456")
        print("    alice / alice789")

        # Authentication flow
        current_student = None
        while not current_student:
            current_student = self.login_ui.show()

        # Main menu loop
        while True:
            print("\n" + "=" * 60)
            print("  Main Menu")
            print("=" * 60)
            print("  [1] Search Available Rooms")
            print("  [2] Book a Room")
            print("  [3] Check In to Room")
            print("  [4] Submit Maintenance Ticket")
            print("  [5] Track Ticket Status")
            print("  [6] View My Bookings")
            print("  [7] Cancel a Booking")
            print("  [8] Logout & Exit")
            print("-" * 60)

            choice = input("  Select option: ").strip()

            if choice == "1":
                date_str, start_time, end_time, min_cap = self.search_ui.enter_criteria()
                self.search_ui.show_available_rooms(date_str, start_time, end_time, min_cap)

            elif choice == "2":
                date_str, start_time, end_time, min_cap = self.search_ui.enter_criteria()
                available = self.search_ui.show_available_rooms(
                    date_str, start_time, end_time, min_cap
                )
                if available:
                    self.booking_ui.start_booking(
                        current_student, available, date_str, start_time, end_time
                    )

            elif choice == "3":
                self.checkin_ui.request_check_in(current_student)

            elif choice == "4":
                self.ticket_ui.submit_issue(current_student)

            elif choice == "5":
                self.ticket_status_ui.enter_ticket_id(current_student)

            elif choice == "6":
                self._view_bookings(current_student)

            elif choice == "7":
                self._cancel_booking(current_student)

            elif choice == "8":
                print("\n  Goodbye! Logging out...")
                break

            else:
                print("\n  ✗ Invalid option. Please try again.")

    def _view_bookings(self, student: Student):
        print("\n" + "-" * 50)
        print("  My Bookings")
        print("-" * 50)
        if not student.bookings:
            print("  No bookings found.")
            return

        for b in student.bookings:
            checkin_status = "Yes" if b.check_in else "No"
            print(f"    [{b.booking_id}] Room {b.room.room_number} | "
                  f"{b.booking_date} {b.start_time}-{b.end_time} | "
                  f"Status: {b.status} | Checked-in: {checkin_status}")

    def _cancel_booking(self, student: Student):
        print("\n" + "-" * 50)
        print("  Cancel a Booking")
        print("-" * 50)

        active = [b for b in student.bookings
                  if b.status in (BookingStatus.CONFIRMED, BookingStatus.PENDING)]
        if not active:
            print("  No active bookings to cancel.")
            return

        for b in active:
            print(f"    [{b.booking_id}] Room {b.room.room_number} | "
                  f"{b.booking_date} {b.start_time}-{b.end_time}")

        booking_id_str = input("\n  Enter Booking ID to cancel: ").strip()
        try:
            booking_id = int(booking_id_str)
        except ValueError:
            print("  ✗ Invalid Booking ID.")
            return

        if self.booking_controller.cancel_booking(booking_id):
            print(f"\n  ✓ Booking {booking_id} cancelled successfully.")
        else:
            print(f"\n  ✗ Could not cancel booking {booking_id}.")


# ============================================================
# AUTOMATED DEMO (runs without user input)
# ============================================================

def run_automated_demo():
    """Demonstrates all use cases without requiring user input."""

    print("\n" + "=" * 70)
    print("  SCFMS - AUTOMATED DEMO")
    print("  Demonstrating all use cases from UML diagrams")
    print("=" * 70)

    # --- Setup ---
    students = []
    s1 = Student(1, "Sasi Sai Nadh Boddu", "sasi@gwu.edu")
    s1.credential = Credential("sasi", "password123")
    students.append(s1)

    s2 = Student(2, "John Smith", "john@gwu.edu")
    s2.credential = Credential("john", "pass456")
    students.append(s2)

    rooms = [
        Room(101, "B101", 30, "Science Building"),
        Room(102, "B102", 50, "Science Building"),
        Room(201, "L201", 20, "Library"),
        Room(301, "E301", 60, "Engineering Hall"),
        Room(501, "C501", 15, "Computer Lab"),
    ]

    # Initialize controllers
    auth = AuthController(students)
    search = RoomSearchController(rooms)
    booking = RoomBookingController(rooms)
    checkin = CheckInController()
    ticket_ctrl = MaintenanceTicketController()
    ticket_status = TicketStatusController(ticket_ctrl)

    # ---- USE CASE 1: Authenticate Credentials ----
    print("\n" + "─" * 60)
    print("  USE CASE 1: Authenticate Credentials")
    print("─" * 60)

    student = auth.authenticate("sasi", "password123")
    if student:
        print(f"  ✓ Login successful: {student}")
    else:
        print("  ✗ Login failed")

    failed = auth.authenticate("sasi", "wrongpassword")
    print(f"  ✗ Login with wrong password: {'Failed (correct)' if not failed else 'ERROR'}")

    # ---- USE CASE 2: Search Available Rooms ----
    print("\n" + "─" * 60)
    print("  USE CASE 2: Search Available Rooms")
    print("─" * 60)

    available = search.search_available_rooms("2026-04-15", "10:00", "12:00")
    print(f"  Found {len(available)} available rooms for 2026-04-15 10:00-12:00:")
    for r in available:
        print(f"    {r}")

    # ---- USE CASE 3: Book Room ----
    print("\n" + "─" * 60)
    print("  USE CASE 3: Book Room")
    print("─" * 60)

    b1 = booking.book_room(student, 101, "2026-04-15", "10:00", "12:00")
    print(f"  Booking result: {b1}")

    b2 = booking.book_room(student, 201, "2026-04-15", "14:00", "16:00")
    print(f"  Booking result: {b2}")

    # Try double-booking same room/time
    b3 = booking.book_room(s2, 101, "2026-04-15", "10:00", "12:00")
    print(f"  Double-booking attempt: {'Rejected (correct)' if not b3 else 'ERROR'}")

    # ---- USE CASE 4: BR Check-In ----
    print("\n" + "─" * 60)
    print("  USE CASE 4: Room Check-In")
    print("─" * 60)

    log = checkin.check_in(b1.booking_id, booking)
    print(f"  Check-in result: {log}")
    print(f"  Booking status after check-in: {b1.status}")
    print(f"  Room status after check-in: {b1.room.status}")

    # Try checking in already checked-in booking
    log2 = checkin.check_in(b1.booking_id, booking)
    print(f"  Re-check-in attempt: {'Rejected (correct)' if not log2 else 'ERROR'}")

    # ---- USE CASE 5: Submit Maintenance Ticket ----
    print("\n" + "─" * 60)
    print("  USE CASE 5: Submit Maintenance Ticket")
    print("─" * 60)

    t1 = ticket_ctrl.create_ticket(student, rooms[0], "HVAC not cooling in B101")
    print(f"  Ticket created: {t1}")

    t2 = ticket_ctrl.create_ticket(student, rooms[2], "Broken window latch in L201")
    print(f"  Ticket created: {t2}")

    # ---- USE CASE 6: Track Ticket Status ----
    print("\n" + "─" * 60)
    print("  USE CASE 6: Track Ticket Status")
    print("─" * 60)

    result = ticket_status.get_status(t1.ticket_id)
    print(f"  Ticket #{result.ticket_id}: {result.current_status}")
    print(f"  History:")
    for h in result.status_history:
        print(f"    [{h.updated_at}] {h.status}")

    # Simulate status updates
    print("\n  --- Updating ticket status ---")
    ticket_ctrl.update_ticket_status(t1.ticket_id, TicketStatus.IN_PROGRESS)
    ticket_ctrl.update_ticket_status(t1.ticket_id, TicketStatus.RESOLVED)

    result = ticket_status.get_status(t1.ticket_id)
    print(f"\n  Ticket #{result.ticket_id} updated history:")
    for h in result.status_history:
        print(f"    [{h.updated_at}] {h.status}")

    # ---- USE CASE 7: Cancel Booking ----
    print("\n" + "─" * 60)
    print("  USE CASE 7: Cancel Booking")
    print("─" * 60)

    print(f"  Before cancel - Booking {b2.booking_id}: {b2.status}")
    booking.cancel_booking(b2.booking_id)
    print(f"  After cancel  - Booking {b2.booking_id}: {b2.status}")

    # Verify room is available again
    available_after = search.search_available_rooms("2026-04-15", "14:00", "16:00")
    room_201_available = any(r.room_id == 201 for r in available_after)
    print(f"  Room L201 available again after cancellation: {room_201_available}")

    # ---- Summary ----
    print("\n" + "=" * 70)
    print("  DEMO COMPLETE - All 6 Use Cases Demonstrated")
    print("=" * 70)
    print(f"\n  Student: {student.name}")
    print(f"  Total bookings:    {len(student.bookings)}")
    print(f"  Active bookings:   {len([b for b in student.bookings if b.status != BookingStatus.CANCELLED])}")
    print(f"  Tickets submitted: {len(student.maintenance_tickets)}")
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import sys

    if "--demo" in sys.argv:
        # Run automated demo (no user input needed)
        run_automated_demo()
    else:
        # Run interactive application
        app = SCFMSApplication()
        app.run()
