# Random Password Generator 🔐

A simple Python project that generates random passwords based on a length specified by the user.

This project was created as part of my **Small Py Projects 🐍** collection to practice Python fundamentals, string manipulation, random generation, functions, loops, and input validation.

---

## ✨ Features

* 🔐 Generate random passwords
* 🔢 Choose the password length
* 🔤 Includes uppercase and lowercase letters
* 🔢 Includes numbers
* 🔣 Includes special characters
* 🔄 Generate multiple passwords in one session
* ⚠️ Validates user input
* 🧩 Simple command-line interface

---

## 🛠️ Technologies Used

* **Python 3**
* `random` module
* `string` module

---

## 📂 Project Structure

```text
Random-Password-Generator/
│
├── password_generator.py
└── README.md
```

---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone <your-repository-url>
```

### 2. Navigate to the project directory

```bash
cd Random-Password-Generator
```

### 3. Run the program

```bash
python password_generator.py
```

---

## 💻 Example

```text
===================================
   🔐 Random Password Generator
===================================

Enter password length: 16

Generated Password:
k$8F!2qP@7xL#9mZ

Generate another password? (y/n): n

Thanks for using the Password Generator! 🔒
```

---

## 🧠 What I Learned

Through this project, I practiced:

* Importing and using Python modules
* Using `string` constants such as letters, digits, and punctuation
* Generating random values
* Creating and calling functions
* Working with loops
* Handling invalid input with `try` and `except`
* Building a simple interactive CLI application
* Using the `if __name__ == "__main__":` pattern

---

## 🔒 Security Note

This project uses Python's `random` module for educational purposes.

For passwords intended for **real-world security**, Python's `secrets` module should be used instead because it is specifically designed for security-sensitive random values.

---

## 🎯 Future Improvements

* [ ] Add a Tkinter GUI
* [ ] Add password strength checking
* [ ] Add options to include/exclude numbers
* [ ] Add options to include/exclude special characters
* [ ] Add a **Copy to Clipboard** button
* [ ] Use Python's `secrets` module for stronger password generation
* [ ] Add customizable password rules

---

## 📜 License

This project is open-source and available for learning and educational purposes.
