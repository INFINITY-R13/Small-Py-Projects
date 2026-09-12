# Caesar Hacker 🔐

A simple Python program that **hacks a Caesar cipher** by trying every possible key and displaying the resulting decrypted messages.

Since a Caesar cipher has only **26 possible keys**, the program can easily perform a brute-force attack and show all possible plaintexts.

## 📌 Features

* 🔓 Brute-force Caesar cipher decryption
* 🔢 Tries all 26 possible keys
* 📝 Accepts encrypted messages from the user
* 🔤 Supports uppercase letters
* ✨ Preserves spaces, numbers, and punctuation
* 💻 Simple command-line interface

## 🛠️ Technologies Used

* **Python 3**
* Built-in Python features only

## 📂 Project Structure

```text
Caesar Hacker/
│
├── main.py
└── README.md
```

## 🚀 How to Run

Make sure Python 3 is installed on your system.

Run the program using:

```bash
python main.py
```

You will be prompted to enter an encrypted message:

```text
Caesar Cipher Hacker
--------------------
Enter the encrypted message to hack:
KHOOR
```

The program will then display all possible decryptions:

```text
Key #0: KHOOR
Key #1: JGNNQ
Key #2: IFMMP
Key #3: HELLO
...
```

In this example, **Key #3** produces the correct plaintext:

```text
HELLO
```

## 🧠 How It Works

The program uses a **brute-force approach**.

1. The encrypted message is entered by the user.
2. The program loops through keys from `0` to `25`.
3. For each key, every letter is shifted backward by that amount.
4. The resulting message is printed alongside its key.
5. The user can identify the correct plaintext from the 26 results.

For example:

```text
Encrypted: KHOOR
Key:       3

K → H
H → E
O → L
O → L
R → O
```

Result:

```text
HELLO
```

## ⏱️ Complexity

Let `n` be the length of the encrypted message.

* **Time Complexity:** `O(26 × n)` → effectively `O(n)`
* **Space Complexity:** `O(n)`

## ⚠️ Limitations

* The program does not automatically determine which result is the correct plaintext.
* It works specifically with the English alphabet defined in `SYMBOLS`.
* Caesar ciphers are intentionally simple and should **not** be used for secure communication.

## 🎯 Purpose

This project is intended as a beginner-friendly exercise for learning:

* Python loops
* String manipulation
* Brute-force techniques
* Caesar cipher concepts
* Basic cryptography

## 📜 License

This project is open-source and available for educational purposes.
