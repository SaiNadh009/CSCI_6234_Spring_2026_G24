# Smart Campus Facility Management System (SCFMS)

This implementation follows the provided UML-based system design:

- Student authentication with hashed credentials.
- Room search and availability checks by date, time, and capacity.
- Room booking flow with slot reservation and booking confirmation.
- Booking state handling (`Pending`, `Confirmed`, `Checked-In`, `Cancelled`, `Completed`).
- Room check-in with booking validation.
- Maintenance ticket submission for campus facilities.
- Ticket status tracking with status history.
- Booking cancellation with automatic slot release.
- Notification simulation for bookings, check-ins, cancellations, and ticket updates.
- Interactive CLI mode and automated demo mode.

## Tech Stack

- Python 3
- Object-Oriented Design (Boundary / Control / Entity pattern)
- Python standard library
- Jupyter Notebook source + standalone Python script

## Run

Start the interactive application:

```bash
python scfms.py
```

Run the automated demo:

```bash
python scfms.py --demo
```

## Demo Users

Interactive application sample users:

- `sasi / password123`
- `nikhil / pass456`
- `alice / alice789`

The app creates these sample students and rooms on startup.

## Sample Rooms

- B101 — Science Building — Capacity 30
- B102 — Science Building — Capacity 50
- L201 — Library — Capacity 20
- L202 — Library — Capacity 40
- E301 — Engineering Hall — Capacity 60
- E302 — Engineering Hall — Capacity 25
- A401 — Auditorium — Capacity 100
- C501 — Computer Lab — Capacity 15

## Project Structure

```text
SCFMS-GitHub-Ready-Updated/
├── SCFMS.ipynb          # Original notebook
├── scfms.py             # Main standalone Python application
├── requirements.txt     # Dependencies (minimal)
├── .gitignore           # Python/Jupyter ignore rules
└── README.md            # Project documentation
```

## Key Functional Areas

- **Authentication**: validates usernames and hashed passwords.
- **Room Search**: filters available rooms and skips rooms under maintenance.
- **Booking Management**: creates, stores, and cancels bookings.
- **Check-In Management**: validates and records room check-ins.
- **Maintenance Ticketing**: creates tickets and stores status history.
- **Notification Service**: simulates user notifications in the console.
- **Boundary Layer**: console-based UI for login, booking, check-in, and ticket tracking.

## Notes

- This project was originally modeled from UML diagrams and implemented in Python.
- `requirements.txt` is intentionally minimal because the project uses the Python standard library.
- The original notebook is included so you can show both the design notebook and the runnable script in your GitHub repository.
- One banner line inside the script mentions `john / pass456`, but the actual seeded interactive user in code is `nikhil / pass456`.

## Suggested GitHub Repository Description

**A Python-based Smart Campus Facility Management System implementing room booking, check-in, and maintenance ticket workflows using object-oriented design principles.**

## Author

**Sasi Sai Nadh Boddu**
