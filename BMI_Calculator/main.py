def calculate_bmi(weight, height_m):
    return weight / (height_m ** 2)


def get_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 24.9:
        return "Normal weight"
    elif bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"


def get_positive_float(prompt):
    value = float(input(prompt))
    if value <= 0:
        raise ValueError
    return value


def get_non_negative_float(prompt):
    value = float(input(prompt))
    if value < 0:
        raise ValueError
    return value


def convert_height_to_meters(feet, inches):
    total_inches = (feet * 12) + inches
    if total_inches <= 0:
        raise ValueError
    return total_inches * 0.0254


def main():
    print("=== BMI Calculator ===")

    try:
        weight = get_positive_float("Enter your weight (kg): ")
        feet = get_non_negative_float("Enter your height (feet): ")
        inches = get_non_negative_float("Enter remaining height (inches): ")

        height_m = convert_height_to_meters(feet, inches)

        bmi = calculate_bmi(weight, height_m)
        category = get_category(bmi)

        print(f"\nYour BMI is: {bmi:.2f}")
        print(f"Category: {category}")

    except ValueError:
        print("Invalid input! Please enter valid positive numbers.")


if __name__ == "__main__":
    main()
