import random
import string


def generate_password(length=12):
    """Generate a random secure password."""
    characters = string.ascii_letters + string.digits + string.punctuation

    password = ''.join(random.choice(characters) for _ in range(length))

    return password


def main():
    print("=" * 35)
    print("   🔐 Random Password Generator")
    print("=" * 35)

    while True:
        try:
            length = int(input("\nEnter password length: "))

            if length < 4:
                print("Password length must be at least 4.")
                continue

            password = generate_password(length)

            print("\nGenerated Password:")
            print(password)

            again = input("\nGenerate another password? (y/n): ").lower()

            if again != "y":
                print("\nThanks for using the Password Generator! 🔒")
                break

        except ValueError:
            print("Please enter a valid number.")


if __name__ == "__main__":
    main()