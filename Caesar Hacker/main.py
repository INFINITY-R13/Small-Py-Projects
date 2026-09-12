# Caesar Hacker

SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

print("Caesar Cipher Hacker")
print("--------------------")
print("Enter the encrypted message to hack:")

message = input().upper()

for key in range(len(SYMBOLS)):
    translated = ''

    for symbol in message:
        if symbol in SYMBOLS:
            num = SYMBOLS.find(symbol)
            num = num - key

            if num < 0:
                num += len(SYMBOLS)

            translated += SYMBOLS[num]
        else:
            translated += symbol

    print(f"Key #{key}: {translated}")