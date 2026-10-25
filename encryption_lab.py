import os
from cryptography.fernet import Fernet, InvalidToken

VAULT = "encrypted_vault"
KEY_FILE = os.path.join(VAULT, "vault.key")

os.makedirs(VAULT, exist_ok=True)

def generate_key():
    if os.path.exists(KEY_FILE):
        print("\nA key already exists.")
        print("Existing key was not replaced.")
        return

    key = Fernet.generate_key()

    with open(KEY_FILE, "wb") as file:
        file.write(key)

    print("\nEncryption key generated successfully.")
    print("Key location:", KEY_FILE)
    print("Keep this key private and make a secure backup.")

def load_key():
    if not os.path.isfile(KEY_FILE):
        print("\nERROR: Encryption key not found.")
        print("Generate a key first.")
        return None

    with open(KEY_FILE, "rb") as file:
        return file.read()

def encrypt_file():
    key = load_key()

    if key is None:
        return

    path = os.path.expanduser(
        input("\nEnter original file path: ").strip()
    )

    if not os.path.isfile(path):
        print("ERROR: File not found.")
        return

    try:
        with open(path, "rb") as file:
            data = file.read()

        encrypted = Fernet(key).encrypt(data)

        filename = os.path.basename(path) + ".enc"
        output = os.path.join(VAULT, filename)

        if os.path.exists(output):
            print("ERROR: Output file already exists.")
            return

        with open(output, "wb") as file:
            file.write(encrypted)

        print("\nFile encrypted successfully.")
        print("Encrypted copy:", output)
        print("Original file was not modified.")

    except (OSError, ValueError) as error:
        print("ERROR:", error)

def decrypt_file():
    key = load_key()

    if key is None:
        return

    path = os.path.expanduser(
        input("\nEnter encrypted file path: ").strip()
    )

    if not os.path.isfile(path):
        print("ERROR: Encrypted file not found.")
        return

    try:
        with open(path, "rb") as file:
            encrypted = file.read()

        decrypted = Fernet(key).decrypt(encrypted)

        filename = os.path.basename(path)

        if filename.endswith(".enc"):
            filename = filename[:-4]
        else:
            filename += ".decrypted"

        output = os.path.join(VAULT, filename)

        if os.path.exists(output):
            print("ERROR: Output file already exists.")
            return

        with open(output, "wb") as file:
            file.write(decrypted)

        print("\nFile decrypted successfully.")
        print("Restored copy:", output)

    except InvalidToken:
        print("ERROR: Invalid key or damaged encrypted file.")
    except OSError as error:
        print("ERROR:", error)

def main():
    while True:
        os.system("clear")
        print("=" * 45)
        print("TORDISSX86 ENCRYPTION LAB v4.8")
        print("=" * 45)
        print("[1] Generate Encryption Key")
        print("[2] Encrypt File")
        print("[3] Decrypt File")
        print("[0] Back to Dashboard")
        print("=" * 45)

        choice = input("Select option: ").strip()

        if choice == "1":
            generate_key()
            input("\nPress ENTER to continue...")
        elif choice == "2":
            encrypt_file()
            input("\nPress ENTER to continue...")
        elif choice == "3":
            decrypt_file()
            input("\nPress ENTER to continue...")
        elif choice == "0":
            break
        else:
            print("Invalid option.")
            input("Press ENTER...")

if __name__ == "__main__":
    main()
