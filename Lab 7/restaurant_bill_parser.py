def clean_dish_name(name):
    """
    Removes the chef's-special markers (*, #, ~) and title-cases the name.
    Returns an empty string if name is not a string (e.g. None).
    """
    if not isinstance(name, str):
        return ""
    name = name.strip()
    for ch in ['*', '#', '~']:
        name = name.replace(ch, '')
    return name.strip().title()


def parse_item_prices(text):
    """
    Parses comma-separated prices into a list of ints.
    Empty entries, non-numeric entries and negative prices are skipped.
    Returns an empty list if text is not a string (e.g. None).
    """
    if not isinstance(text, str):
        return []
    prices = []
    for part in text.split(','):
        part = part.strip()
        if not part:
            continue
        try:
            price = int(part)
        except ValueError:
            continue
        if price >= 0:
            prices.append(price)
    return prices


def split_amount(text):
    """
    Splits 'TOTAL/PEOPLE' into the amount each person pays.
    Returns None if the input is not a string, is not in the form
    'TOTAL/PEOPLE', has non-integer values, a negative total,
    or fewer than one person (including zero).
    """
    if not isinstance(text, str):
        return None
    parts = text.split('/')
    if len(parts) != 2:
        return None
    try:
        total = int(parts[0].strip())
        people = int(parts[1].strip())
    except ValueError:
        return None
    if total < 0 or people < 1:
        return None
    return total // people


def main():
    print("==== Running clean_dish_name ====")
    value = input("Enter a dish name from the menu (e.g. *paneer tikka*): ")
    print("Dish name:", clean_dish_name(value))

    print("\n==== Running parse_item_prices ====")
    value = input("Enter item prices separated by commas (e.g. 250,180,320): ")
    print("Item prices:", parse_item_prices(value))

    print("\n==== Running split_amount ====")
    value = input("Enter the bill and number of people as TOTAL/PEOPLE (e.g. 1200/4): ")
    result = split_amount(value)
    if result is None:
        print("Invalid input: use TOTAL/PEOPLE with whole numbers and at least 1 person.")
    else:
        print("Each person pays:", result)


if __name__ == "__main__":
    main()