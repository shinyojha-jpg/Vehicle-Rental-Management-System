from pathlib import Path

DATA_FILE = Path(__file__).with_name("vehicles.txt")
DISCOUNT_DAYS = 7
DISCOUNT_RATE = 0.10


class Vehicle:
    #Stores details of a vehicle

    def __init__(self, vehicle_id, vehicle_type, model, rate_per_day, available=True):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.model = model
        self.rate_per_day = float(rate_per_day)
        self.available = available

    def to_record(self):
        #Convert vehicle details into a text record.
        return (
            f"{self.vehicle_id}|{self.vehicle_type}|"
            f"{self.model}|{self.rate_per_day}|"
            f"{int(self.available)}"
        )

    @classmethod
    def from_record(cls, record):
        #Create a Vehicle object from a saved record.
        parts = record.strip().split("|")

        if len(parts) != 5:
            raise ValueError("Invalid vehicle record")

        return cls(
            parts[0],
            parts[1],
            parts[2],
            float(parts[3]),
            parts[4] == "1"
        )


class RentalManager:
    #Manages vehicles and rental operations.

    def __init__(self):
        self.vehicles = []
        self.rentals = {}
        self.load_vehicles()

    def load_vehicles(self):
        #Load saved vehicle details from the file.
        if not DATA_FILE.exists():
            DATA_FILE.write_text("", encoding="utf-8")
            return

        self.vehicles = []

        with DATA_FILE.open("r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                try:
                    vehicle = Vehicle.from_record(line)
                    self.vehicles.append(vehicle)
                except (ValueError, IndexError):
                    print("Warning: Invalid record skipped.")

    def save_vehicles(self):
        #Save all vehicle details to the file
        with DATA_FILE.open("w", encoding="utf-8") as file:
            for vehicle in self.vehicles:
                file.write(vehicle.to_record() + "\n")

    def generate_vehicle_id(self):
        #Generate IDs such as V1, V2, V3
        largest = 0

        for vehicle in self.vehicles:
            try:
                number = int(vehicle.vehicle_id[1:])
                largest = max(largest, number)
            except (ValueError, IndexError):
                continue

        return f"V{largest + 1}"

    def find_vehicle(self, vehicle_id):
        #Find a vehicle using its ID.
        for vehicle in self.vehicles:
            if vehicle.vehicle_id.lower() == vehicle_id.lower():
                return vehicle

        return None

    def add_vehicle(self):
        print("\n ADD VEHICLE ")

        vehicle_type = input(
            "Vehicle type (Car/Bike/Scooter): "
        ).strip().title()

        if vehicle_type not in ["Car", "Bike", "Scooter"]:
            print("Invalid vehicle type.")
            return

        model = input("Enter vehicle model: ").strip()

        if not model or "|" in model:
            print("Model cannot be empty or contain '|'.")
            return

        try:
            rate = float(input("Rate per day (Rs.): "))

            if rate <= 0:
                raise ValueError

        except ValueError:
            print("Enter a valid rate greater than zero.")
            return

        vehicle_id = self.generate_vehicle_id()

        vehicle = Vehicle(
            vehicle_id,
            vehicle_type,
            model,
            rate,
            True
        )

        self.vehicles.append(vehicle)
        self.save_vehicles()

        print("\nVehicle added successfully!")
        print(f"Vehicle ID: {vehicle_id}")
        print(f"Type: {vehicle_type}")
        print(f"Model: {model}")
        print(f"Rate per day: Rs. {rate:.2f}")
        print("Status: Available")

    def show_vehicles(self, available_only=False):
        #Display all vehicles or only available vehicles
        vehicles = [
            vehicle for vehicle in self.vehicles
            if not available_only or vehicle.available
        ]

        if not vehicles:
            print("\nNo vehicles to display.")
            return

        print("\n" + "-" * 68)
        print(
            f"{'ID':<6}{'Type':<12}{'Model':<18}"
            f"{'Rate/Day':<15}{'Status'}"
        )
        print("-" * 68)

        for vehicle in vehicles:
            status = (
                "Available" if vehicle.available else "Rented"
            )

            print(
                f"{vehicle.vehicle_id:<6}"
                f"{vehicle.vehicle_type:<12}"
                f"{vehicle.model:<18}"
                f"Rs. {vehicle.rate_per_day:<10.2f}"
                f"{status}"
            )

        print("-" * 68)

    def rent_vehicle(self):
        print("\n RENT VEHICLE ")

        vehicle_id = input("Enter vehicle ID: ").strip()
        vehicle = self.find_vehicle(vehicle_id)

        if vehicle is None:
            print("Vehicle ID not found.")
            return

        if not vehicle.available:
            print(f"Vehicle {vehicle.vehicle_id} is not available.")
            return

        customer = input("Enter customer name: ").strip()

        if not customer:
            print("Customer name cannot be empty.")
            return

        try:
            days = int(input("Enter rental days: "))

            if days < 1:
                raise ValueError

        except ValueError:
            print("Rental days must be a whole number of at least 1.")
            return

        subtotal = vehicle.rate_per_day * days

        if days >= DISCOUNT_DAYS:
            discount = subtotal * DISCOUNT_RATE
        else:
            discount = 0

        total = subtotal - discount

        # Mark vehicle as rented.
        vehicle.available = False

        # Store rental details in a dictionary.
        self.rentals[vehicle.vehicle_id] = {
            "customer": customer,
            "days": days,
            "bill": total
        }

        self.save_vehicles()

        print("\n RENTAL BILL")
        print(f"Customer       : {customer}")
        print(f"Vehicle ID     : {vehicle.vehicle_id}")
        print(f"Vehicle type   : {vehicle.vehicle_type}")
        print(f"Model          : {vehicle.model}")
        print(f"Rental days    : {days}")
        print(f"Rate per day   : Rs. {vehicle.rate_per_day:.2f}")
        print(f"Subtotal       : Rs. {subtotal:.2f}")
        print(f"Discount       : Rs. {discount:.2f}")
        print(f"Final bill     : Rs. {total:.2f}")
        print("")

        print(
            f"{vehicle.vehicle_id} rented to {customer} "
            f"for {days} day(s)."
        )

    def return_vehicle(self):
        print("\n RETURN VEHICLE ")

        vehicle_id = input("Enter vehicle ID to return: ").strip()
        vehicle = self.find_vehicle(vehicle_id)

        if vehicle is None:
            print("Vehicle ID not found.")
            return

        if vehicle.available:
            print(f"Vehicle {vehicle.vehicle_id} is already available.")
            return

        rental = self.rentals.pop(vehicle.vehicle_id, None)

        vehicle.available = True
        self.save_vehicles()

        if rental:
            print(
                f"Vehicle {vehicle.vehicle_id} returned by "
                f"{rental['customer']}."
            )
        else:
            print(f"Vehicle {vehicle.vehicle_id} returned successfully.")

        print("Status: Available")

    def run(self):
        """Display the menu until the user chooses Exit."""
        while True:
            print("\n")
            print("   VEHICLE RENTAL MANAGEMENT SYSTEM")
            print("")
            print("1. Add Vehicle")
            print("2. Rent Vehicle")
            print("3. Return Vehicle")
            print("4. View All Vehicles")
            print("5. View Available Vehicles")
            print("6. Exit")
            print("")

            choice = input("Enter your choice (1-6): ").strip()

            if choice == "1":
                self.add_vehicle()

            elif choice == "2":
                self.rent_vehicle()

            elif choice == "3":
                self.return_vehicle()

            elif choice == "4":
                self.show_vehicles()

            elif choice == "5":
                self.show_vehicles(available_only=True)

            elif choice == "6":
                self.save_vehicles()
                print("Data saved successfully.")
                print("Thank you for using the system!")
                break

            else:
                print("Invalid choice. Please select 1 to 6.")


if __name__ == "__main__":
    manager = RentalManager()
    manager.run()
