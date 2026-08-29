def generate_fibonacci(n):
    """Generate the first n numbers of the Fibonacci sequence (max n = 13)."""
    if n <= 0:
        return []
    
    sequence = []
    a, b = 0, 1
    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b
    return sequence


if __name__ == "__main__":
    try:
        n = int(input("Enter how many Fibonacci numbers you want (1 to 13): "))
        
        if n < 1 or n > 13:
            print("Error: n must be between 1 and 13.")
        else:
            result = generate_fibonacci(n)
            print(f"First {n} Fibonacci numbers:")
            print(result)
            
    except ValueError:
        print("Invalid input. Please enter an integer.")