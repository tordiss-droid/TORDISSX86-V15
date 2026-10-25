import os
import secrets
import string

def generate_password(length):
    if length < 12 or length > 64:
        raise ValueError("Length must be between 12 and 64.")

    groups = [
        string.ascii_lowercase,
        string.ascii_uppercase,
        string.digits,
        "!@#$%^&*()-_=+"
    ]

    password = [
        secrets.choice(group)
        for group in groups
    ]

    alphabet = "".join(groups)

    while len(password) < length:
        password.append(secrets.choice(alphabet))

    secrets.SystemRandom().shuffle(password)

    return "".join(password)

def main():
    while True:
        os.system("clear")
        print("=" * 45)
        print("TORDISSX86 SECURE PASSWORD GENERATOR v4.7")
        print("=" * 45)
        print("[1] Generate Password")
        print("[2] Generate Multiple Passwords")
        print("[0] Back to Dashboard")

        choice = input("\nSelect option: ").strip()

        if choice in ("1", "2"):
            try:
                length = int(input("Password length (12-64): "))

                if choice == "1":
                    count = 1
                else:
                    count = int(input("Number of passwords (1-5): "))

                if not 1 <= count <= 5:
                    print("ERROR: Choose between 1 and 5.")
                else:
                    print("\nGENERATED PASSWORDS:")
                    print("-" * 45)

                    for number in range(count):
                        password = generate_password(length)
                        print(f"{number + 1}. {password}")

                    print("-" * 45)
                    print("Passwords are not saved.")

            except ValueError as error:
                print("ERROR:", error)

            input("\nPress ENTER to continue...")

        elif choice == "0":
            break
        else:
            print("Invalid option.")
            input("Press ENTER...")

if __name__ == "__main__":
    main()
