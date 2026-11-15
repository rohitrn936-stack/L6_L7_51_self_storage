def parse_rental(text):
    if not text or not isinstance(text, str):
        return None
    if ":" not in text:
        return None
    parts = text.split(":")
    if len(parts) != 2:
        return None
    unit, months_str = parts
    unit = unit.strip().title()
    try:
        months = float(months_str)
    except ValueError:
        return None
    if months < 0:
        return None
    return unit.strip().title(), months


def duration_average(months_csv):
    if not months_csv or not isinstance(months_csv, str):
        return None
    values = []
    for r in months_csv.split(","):
        r = r.strip()
        if r == "":
            return None
        try:
            values.append(int(r))
        except ValueError:
            return None
    if len(values) == 0:
        return None
    return sum(values) // len(values)


def payable_rent(text):
    if not text or not isinstance(text, str):
        return None
    if "|" not in text:
        return None
    parts = text.split("|")
    if len(parts) != 2:
        return None
    try:
        rent = float(parts[0].strip())
        discount = float(parts[1].strip())
    except ValueError:
        return None
    if rent < 0 or discount < 0:
        return None
    total = rent * 1.18 - discount
    return max(total, 0)


def main():
    print("==== Running parse_rental ====")
    user_input = input("Enter unit:months (e.g. medium:6): ")
    result = parse_rental(user_input)
    print("Unit and Months:", result)

    print("\n==== Running duration_average ====")
    user_input = input("Enter rental months as CSV (e.g. 3,6,12): ")
    result = duration_average(user_input)
    print("Average Duration:", result)

    print("\n==== Running payable_rent ====")
    user_input = input("Enter rent|discount (e.g. 2400|200): ")
    result = payable_rent(user_input)
    print("Payable Rent:", result)


if __name__ == "__main__":
    main()