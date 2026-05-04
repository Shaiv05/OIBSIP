import json
from datetime import datetime


FILE_NAME = "bmi_data.json"


def calculate_bmi(weight, height_m):
    return weight / (height_m ** 2)


def get_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def get_float_input(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Please enter a positive number.")
            else:
                return value
        except ValueError:
            print("Invalid input! Please enter a number.")


def get_height_input():
    while True:
        try:
            feet = int(input("Enter your height (feet): "))
            inches = int(input("Enter remaining height (inches): "))

            if feet < 0 or inches < 0:
                print("Height cannot be negative.")
                continue

            if inches >= 12:
                print("Inches should be less than 12.")
                continue

            if feet == 0 and inches == 0:
                print("Height cannot be zero.")
                continue

            return feet, inches

        except ValueError:
            print("Invalid input! Please enter whole numbers.")


def load_data():
    try:
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_data(data):
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)


def show_history(data):
    if not data:
        print("\nNo history available.\n")
        return

    print("\n=== BMI HISTORY ===")
    for entry in data:
        print(f"{entry['date']} | BMI: {entry['bmi']:.2f} | {entry['category']}")
    print("====================\n")


def run_bmi(data):
    weight = get_float_input("Enter your weight (kg): ")
    feet, inches = get_height_input()

    total_inches = (feet * 12) + inches
    height_m = total_inches * 0.0254

    bmi = calculate_bmi(weight, height_m)
    category = get_category(bmi)

    print("\n--- RESULT ---")
    print(f"Your BMI is: {bmi:.2f}")
    print(f"Category: {category}")
    print("----------------\n")

    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "bmi": bmi,
        "category": category
    }

    data.append(entry)
    save_data(data)


def main():
    data = load_data()

    print("=== BMI Tracker ===")

    while True:
        print("1. Calculate BMI")
        print("2. View History")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            run_bmi(data)
        elif choice == "2":
            show_history(data)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()