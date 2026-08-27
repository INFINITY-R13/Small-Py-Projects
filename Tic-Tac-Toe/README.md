# Tic Tac Toe

A simple console-based Tic Tac Toe game written in Python.

## Description

Play the classic 3×3 Tic Tac Toe game against a friend in the terminal.  
Players take turns placing **X** and **O** on the board. The first player to get three of their marks in a row (horizontally, vertically, or diagonally) wins. If the board fills up with no winner, the game ends in a draw.

## Features

- Clean and easy-to-read board display
- Input validation (prevents invalid or already occupied moves)
- Win detection (rows, columns, diagonals)
- Draw detection
- Clear turn indicators
- Simple numbered board positions (1–9)

## Requirements

- Python 3.6 or higher  
No external libraries required.

## How to Run

1. Save the code as `tictactoe.py`
2. Open a terminal in the same folder
3. Run the game:

```bash
python tictactoe.py
```

## How to Play

1. The board positions are numbered like this:

```
 1 | 2 | 3 
-----------
 4 | 5 | 6 
-----------
 7 | 8 | 9 
```

2. Player **X** always starts first.
3. On your turn, enter a number between **1** and **9** to place your mark.
4. The game will automatically detect a win or a draw and end.

## Example Gameplay

```
Welcome to Tic Tac Toe!
Positions are numbered like this:
 1 | 2 | 3 
-----------
 4 | 5 | 6 
-----------
 7 | 8 | 9 

   |   |   
-----------
   |   |   
-----------
   |   |   

Player X, enter your move (1-9): 5
```

## License

This project is open source and free to use.