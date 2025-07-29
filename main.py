import argparse
import getpass
import json
import os
from generator import generate_password
from cryptography.fernet import Fernet

# --- Key Management ---
KEY_FILE = "secret.key"
VAULT_FILE = "vault.enc"

def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)

def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    else:
        print("❌ secret.key not found. Run the program once to generate it.")
        exit()

# --- Vault Encryption/Decryption ---
def load_vault():
    if not os.path.exists(VAULT_FILE):
        return {}
    try:
        with open(VAULT_FILE, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = Fernet(load_key()).decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    except Exception as e:
        print(f"❌ Failed to load vault: {e}")
        exit()

def save_vault(vault_data):
    try:
        encrypted_data = Fernet(load_key()).encrypt(json.dumps(vault_data).encode())
        with open(VAULT_FILE, "wb") as f:
            f.write(encrypted_data)
    except Exception as e:
        print(f"❌ Failed to save vault: {e}")
        exit()

# --- Setup ---
generate_key()
vault = load_vault()
master_password = getpass.getpass("Enter master password: ")  # Placeholder (not tied to encryption yet)

# --- CLI Commands ---
parser = argparse.ArgumentParser(description="Simple CLI Password Manager")
subparsers = parser.add_subparsers(dest="command")

# Add command
add_parser = subparsers.add_parser("add")
add_parser.add_argument("--site", required=True)
add_parser.add_argument("--username", required=True)
pw_group = add_parser.add_mutually_exclusive_group(required=True)
pw_group.add_argument("--password", help="Password to store")
pw_group.add_argument("--generate", type=int, nargs="?", const=16, help="Generate a random password (default 16 chars)")

# View command
view_parser = subparsers.add_parser("view")
view_parser.add_argument("--site", required=True)

# List command
subparsers.add_parser("list")

# Delete command
delete_parser = subparsers.add_parser("delete")
delete_parser.add_argument("--site", required=True)

args = parser.parse_args()

# --- Command Handling ---
if args.command == "add":
    password = args.password if args.password else generate_password(args.generate)
    if not password:
        print("Error: Must provide --password or --generate")
        exit()
    if args.generate:
        print(f"Generated password: {password}")

    if args.site in vault:
        print("Error: This site already exists.")
    else:
        vault[args.site] = {"username": args.username, "password": password}
        save_vault(vault)
        print("✅ Credential saved successfully.")

elif args.command == "view":
    if args.site in vault:
        print(f"Username: {vault[args.site]['username']}")
        print(f"Password: {vault[args.site]['password']}")
    else:
        print("❌ Site not found.")

elif args.command == "list":
    print("Stored sites:")
    for site in vault:
        print(f"- {site}")

elif args.command == "delete":
    if args.site in vault:
        del vault[args.site]
        save_vault(vault)
        print("✅ Entry deleted.")
    else:
        print("❌ Site not found.")

else:
    parser.print_help()
