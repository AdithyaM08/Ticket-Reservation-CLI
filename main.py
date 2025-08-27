import json
import os
from datetime import datetime

# ------------------------------
# File names
# ------------------------------
USERS_FILE = "users.json"
BOOKINGS_FILE = "bookings.json"
ROUTES_FILE = "routes.json"

# ------------------------------
# Helper functions for file handling
# ------------------------------
def load_data(file_name):
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            json.dump([], f)
    with open(file_name, "r") as f:
        return json.load(f)

def save_data(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

# ------------------------------
# User class
# ------------------------------
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @staticmethod
    def register():
        username = input("Enter username: ")
        password = input("Enter password: ")
        users = load_data(USERS_FILE)

        if any(u["username"] == username for u in users):
            print("Username already exists! Try another.")
            return None

        new_user = {"username": username, "password": password}
        users.append(new_user)
        save_data(USERS_FILE, users)
        print("Registration successful!")
        return User(username, password)

    @staticmethod
    def login():
        username = input("Enter username: ")
        password = input("Enter password: ")
        users = load_data(USERS_FILE)

        for u in users:
            if u["username"] == username and u["password"] == password:
                print("Login successful!")
                return User(username, password)
        print("Invalid credentials!")
        return None

# ------------------------------
# Route class
# ------------------------------
class Route:
    def __init__(self, route_id, source, destination, seats, fare):
        self.route_id = route_id
        self.source = source
        self.destination = destination
        self.seats = seats
        self.fare = fare

    @staticmethod
    def load_routes():
        data = load_data(ROUTES_FILE)
        return [Route(**r) for r in data]

    @staticmethod
    def save_routes(routes):
        data = [r.__dict__ for r in routes]
        save_data(ROUTES_FILE, data)

    @staticmethod
    def show_routes(routes):
        print("\nAvailable Routes:")
        for r in routes:
            print(f"ID: {r.route_id}, {r.source} -> {r.destination}, Seats: {r.seats}, Fare: ${r.fare}")

# ------------------------------
# Booking class
# ------------------------------
class Booking:
    def __init__(self, username, route_id, seats_booked, booking_time):
        self.username = username
        self.route_id = route_id
        self.seats_booked = seats_booked
        self.booking_time = booking_time

    @staticmethod
    def book_ticket(user):
        routes = Route.load_routes()
        Route.show_routes(routes)
        route_id = int(input("Enter route ID to book: "))
        seats = int(input("Enter number of seats: "))

        route = next((r for r in routes if r.route_id == route_id), None)
        if not route:
            print("Invalid Route ID!")
            return
        if seats > route.seats:
            print(f"Only {route.seats} seats available.")
            return

        # Reduce available seats
        route.seats -= seats
        Route.save_routes(routes)

        # Save booking
        bookings = load_data(BOOKINGS_FILE)
        booking = Booking(user.username, route_id, seats, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        bookings.append(booking.__dict__)
        save_data(BOOKINGS_FILE, bookings)
        print(f"Booking successful! Total fare: ${seats * route.fare}")

    @staticmethod
    def cancel_booking(user):
        bookings = load_data(BOOKINGS_FILE)
        user_bookings = [b for b in bookings if b["username"] == user.username]

        if not user_bookings:
            print("No bookings found!")
            return

        print("\nYour Bookings:")
        for idx, b in enumerate(user_bookings):
            print(f"{idx+1}. Route ID: {b['route_id']}, Seats: {b['seats_booked']}, Time: {b['booking_time']}")

        choice = int(input("Enter booking number to cancel: "))
        if choice < 1 or choice > len(user_bookings):
            print("Invalid choice!")
            return

        booking_to_cancel = user_bookings[choice - 1]

        # Restore seats
        routes = Route.load_routes()
        route = next((r for r in routes if r.route_id == booking_to_cancel["route_id"]), None)
        if route:
            route.seats += booking_to_cancel["seats_booked"]
            Route.save_routes(routes)

        # Remove booking
        bookings.remove(booking_to_cancel)
        save_data(BOOKINGS_FILE, bookings)
        print("Booking canceled successfully!")

    @staticmethod
    def view_bookings(user):
        bookings = load_data(BOOKINGS_FILE)
        user_bookings = [b for b in bookings if b["username"] == user.username]
        if not user_bookings:
            print("No bookings found!")
            return
        print("\nYour Bookings:")
        for b in user_bookings:
            print(f"Route ID: {b['route_id']}, Seats: {b['seats_booked']}, Time: {b['booking_time']}")

# ------------------------------
# Initialize routes
# ------------------------------
def initialize_routes():
    if os.path.exists(ROUTES_FILE) and load_data(ROUTES_FILE):
        return
    sample_routes = [
        {"route_id": 1, "source": "CityA", "destination": "CityB", "seats": 50, "fare": 20},
        {"route_id": 2, "source": "CityB", "destination": "CityC", "seats": 40, "fare": 25},
        {"route_id": 3, "source": "CityA", "destination": "CityC", "seats": 30, "fare": 30}
    ]
    save_data(ROUTES_FILE, sample_routes)

# ------------------------------
# Main CLI
# ------------------------------
def main():
    initialize_routes()
    user = None

    while True:
        if not user:
            print("\n--- Welcome to Ticket Booking System ---")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Enter choice: ")
            if choice == "1":
                user = User.register()
            elif choice == "2":
                user = User.login()
            elif choice == "3":
                break
            else:
                print("Invalid choice!")
        else:
            print(f"\n--- Welcome {user.username} ---")
            print("1. View Routes")
            print("2. Book Ticket")
            print("3. Cancel Booking")
            print("4. View My Bookings")
            print("5. Logout")
            choice = input("Enter choice: ")
            if choice == "1":
                routes = Route.load_routes()
                Route.show_routes(routes)
            elif choice == "2":
                Booking.book_ticket(user)
            elif choice == "3":
                Booking.cancel_booking(user)
            elif choice == "4":
                Booking.view_bookings(user)
            elif choice == "5":
                user = None
            else:
                print("Invalid choice!")

if __name__ == "__main__":
    main()
