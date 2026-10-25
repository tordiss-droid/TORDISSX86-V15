import os
import getpass
import re

COMMON_PASSWORDS = {
    "password", "12345678", "123456789",
    "qwerty123", "admin123", "welcome123"
}

def analyze_password():
    password = getpass.getpass("\nEnter a test password: ")

    if not password:
        print("No password entered.")
        return

    score = 0
    recommendations = []

    if len(password) >= 12:
        score += 2
    else:
        recommendations.append("Use at least 12 characters.")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        recommendations.append("Include lowercase letters.")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        recommendations.append("Include uppercase letters.")

    if re.search(r"[0-9]", password):
        score += 1
    else:
        recommendations.append("Include numbers.")

    if re.search(r"[^a-zA-Z0-9]", password):
        score += 1
    else:
        recommendations.append("Include special characters.")

    if password.lower() in COMMON_PASSWORDS:
        score = 0
        recommendations.append("Avoid common passwords.")

    if score >= 6:
        strength = "STRONG"
    elif score >= 4:
        strength = "MODERATE"
    else:
        strength = "WEAK"

    print("\n" + "=" * 42)
    print("TORDISSX86 PASSWORD SECURITY LAB")
    print("=" * 42)
    print("Length:", len(password))
    print("Strength:", strength)

    print("\nRecommendations:")
    if recommendations:
        for item in recommendations:
            print("-", item)
    else:
        print("Your test password meets the basic checks.")

    print("=" * 42)
    print("Password was not saved.")

def main():
    while True:
        os.system("clear")
        print("=" * 42)
        print("TORDISSX86 PASSWORD SECURITY LAB v4.6")
        print("=" * 42)
        print("[1] Check Password Strength")
        print("[0] Back to Dashboard")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            analyze_password()
            input("\nPress ENTER to continue...")
        elif choice == "0":
            break
        else:
            print("Invalid option.")
            input("Press ENTER...")

if __name__ == "__main__":
    main()
