# Caesar-Cipher

SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

print("This is a caesar cipher program.")

while True:
    print("Do u want to encrypt or decrypt?")
    response = input().lower()
    if response.startswith('e'):
        mode = 'encrypt'
        break
    elif response.startswith('d'):
        mode = 'decrypt'
        break
    print("Please enter the letter 'e' or 'd'.")


while True:
    max_key = len(SYMBOLS) - 1
    print(f"Please enter key from 0 - {max_key}.") 
    user_input = input()
    if user_input.isdigit():
        key = int(user_input)
        if 0 <= key <= max_key:
            break
    print("Invalid input. Please enter a valid number.")

print(f"Enter the message to {mode}:")  
message = input().upper()

translated = ''

for symbol in message:
    if symbol in SYMBOLS:
        num = SYMBOLS.find(symbol)
        if mode == 'encrypt':
            num = num + key
        elif mode == 'decrypt':
            num = num - key

        num = num % len(SYMBOLS)    

        translated = translated + SYMBOLS[num]
    else:
        translated = translated + symbol

print(translated)            