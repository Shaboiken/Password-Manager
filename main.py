import argparse
import getpass
import json
import os
from generator import generate_password

VAULT_FILE = "vault.json"

# Check if vault file exists, create if not
if not os.path.exists(VAULT_FILE):
    with open(VAULT_FILE, "w") as f:
        json.dump({}, f)

# Load the vault
with open(VAULT_FILE, "r") as f:
    vault = json.load(f)

# Get master password (not stored yet — just simulating)
master_password = getpass.getpass("Enter master password:")

# Set up argparse
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

# Command handling
if args.command == "add":
    # Choose password from input or generated
    if args.password:
        password = args.password
    elif args.generate:
        password = generate_password(args.generate)
        print(f"Generated password: {password}")
    else:
        print("Error: You must provide --password or --generate")
        exit()

    # Add to vault
    if args.site in vault:
        print("Error: This site already exists in the vault.")
    else:
        vault[args.site] = {
            "username": args.username,
            "password": password
        }
        with open(VAULT_FILE, "w") as f:
            json.dump(vault, f)
        print("Credential saved successfully.")


elif args.command == "view":
    if args.site in vault:
        print(f"Username: {vault[args.site]['username']}")
        print(f"Password: {vault[args.site]['password']}")
    else:
        print("Site not found.")

elif args.command == "list":
    print("Stored sites:")
    for site in vault:
        print(f"- {site}")

elif args.command == "delete":
    if args.site in vault:
        del vault[args.site]
        with open(VAULT_FILE, "w") as f:
            json.dump(vault, f)
        print("Deleted.")
    else:
        print("Site not found.")
else:
    parser.print_help()
