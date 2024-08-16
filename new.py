import hashlib

def md5_hash_string(input_string):
    """Generate MD5 hash of the input string."""
    return hashlib.md5(input_string.encode()).hexdigest()

def main():
    # Get user input
    user_string = input("Enter a string to hash: ")
    hash_to_check = input("Enter the hash to compare with: ")

    # Generate MD5 hash of the user input
    hashed_string = md5_hash_string(user_string)

    # Display the result
    print(f'Generated MD5 hash: {hashed_string}')
    if hashed_string == hash_to_check:
        print("The hashes match!")
    else:
        print("The hashes do not match.")

if __name__ == "__main__":
    main()
