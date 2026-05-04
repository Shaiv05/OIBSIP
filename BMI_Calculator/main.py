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


def run_bmi():
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


def main():
    print("=== BMI Calculator ===")

    while True:
        run_bmi()

        choice = input("Do you want to calculate again? (y/n): ").lower()

        if choice != 'y':
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()