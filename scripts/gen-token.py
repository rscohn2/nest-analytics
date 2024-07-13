import secrets


def generate_secret_token():
    # Generate a secure token. This example generates a 32-byte (256-bit)
    # token. You can adjust the length as needed.
    token = secrets.token_hex(32)
    print(f"Generated secret token: {token}")
    return token


if __name__ == "__main__":
    generate_secret_token()
