from collections import UserDict
from datetime import datetime, timedelta, date

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, name):
        super().__init__(name)

class Phone(Field):
    def __init__(self, number):
        self.validate(number)
        super().__init__(number)

    @staticmethod
    def validate(number):
        if not number.isdigit() or len(number) != 10:
            raise ValueError("Wrong format! Phone number must be 10 digits long.")

class Birthday(Field):
    def __init__(self, value):
        self.validate(value)
        self.date = datetime.strptime(value, "%d.%m.%Y").date()
        super().__init__(value)

    @staticmethod
    def validate(value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, removed_phone):
        self.phones = [phone for phone in self.phones if phone.value != removed_phone]

    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Phone number not found.")

    def find_phone(self, this_phone):
        for phone in self.phones:
            if phone.value == this_phone:
                return phone
        return None

    def add_birthday(self, date):
        self.birthday = Birthday(date)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name not in self.data:
            raise KeyError('Name not found')
        del self.data[name]

    def get_upcoming_birthdays(self):
        def find_next_weekday(start_date, weekday):
            days_ahead = weekday - start_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return start_date + timedelta(days=days_ahead)

        def adjust_for_weekend(birthday):
            if birthday.weekday() >= 5:
                return find_next_weekday(birthday, 0)
            return birthday

        upcoming_birthdays = []
        today = datetime.today().date()

        for record in self.data.values():
            if record.birthday:
                user_birthday = record.birthday.date
                next_birthday = user_birthday.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = user_birthday.replace(year=today.year + 1)

                if 0 <= (next_birthday - today).days <= 7:
                    next_birthday = adjust_for_weekend(next_birthday)
                    upcoming_birthdays.append({"name": record.name.value, "congratulation_date": next_birthday.strftime("%d.%m.%Y")})

        return upcoming_birthdays

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            return str(e)
    return wrapper

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday {birthday} added to contact {name}."
    return f"No contact with name {name} found."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is on {record.birthday.value}"
    return f"No birthday information for {name}."

@input_error
def birthdays(book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    result = "Upcoming birthdays:\n"
    result += "\n".join(f"{record['name']}: {record['congratulation_date']}" for record in upcoming_birthdays)
    return result

@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return f"Phone {phone} added to contact {name}."
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return f"Contact {name} with phone {phone} added."

@input_error
def change_contact(args, book):
    name, new_phone = args
    record = book.find(name)
    if record:
        old_phone = record.phones[0].value
        record.edit_phone(old_phone, new_phone)
        return f"Phone number for {name} changed to {new_phone}."
    return f"No contact with name {name} found."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.phones:
        phones = '; '.join(phone.value for phone in record.phones)
        return f"{name}'s phone numbers are: {phones}"
    return f"No phone numbers for {name} found."


@input_error
def show_all(book):
    if not book.data:
        return "No contacts found."
    result = "Contacts:\n"
    for name, record in book.data.items():
        result += str(record) + "\n"
    return result.strip()

@input_error
def parse_input(user_input):
    user_input = user_input.strip()
    cmd, *args = user_input.split()
    cmd = cmd.lower()
    return cmd, args

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        cmd, args = parse_input(user_input)

        if cmd in ["close", "exit"]:
            print("Good bye!")
            break
        elif cmd == "hello":
            print("How can I help you?")
        elif cmd == "add":
            if len(args) < 2:
                print("Invalid command format. Use: add [name] [phone]")
            else:
                print(add_contact(args, book))
        elif cmd == "change":
            if len(args) < 2:
                print("Invalid command format. Use: change [name] [new phone]")
            else:
                print(change_contact(args, book))
        elif cmd == "phone":
            if len(args) < 1:
                print("Invalid command format. Use: phone [name]")
            else:
                print(show_phone(args, book))
        elif cmd == "all":
            print(show_all(book))
        elif cmd == "add-birthday":
            if len(args) < 2:
                print("Invalid command format. Use: add-birthday [name] [birthday]")
            else:
                print(add_birthday(args, book))
        elif cmd == "show-birthday":
            if len(args) < 1:
                print("Invalid command format. Use: show-birthday [name]")
            else:
                print(show_birthday(args, book))
        elif cmd == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
