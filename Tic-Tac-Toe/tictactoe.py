def print_board(board):
    print("\n")
    for i in range(3):
        print(f" {board[i][0]} | {board[i][1]} | {board[i][2]} ")
        if i < 2:
            print("-----------")
    print("\n")

def check_win(board, player):
    # Check rows
    for row in board:
        if all(cell == player for cell in row):
            return True
    # Check columns
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    # Check diagonals
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2 - i] == player for i in range(3)):
        return True
    return False

def check_draw(board):
    return all(cell != " " for row in board for cell in row)

def get_move(board, player):
    while True:
        try:
            move = input(f"Player {player}, enter your move (1-9): ").strip()
            pos = int(move) - 1
            if pos < 0 or pos > 8:
                print("Please enter a number between 1 and 9.")
                continue
            row, col = divmod(pos, 3)
            if board[row][col] != " ":
                print("That spot is already taken. Try again.")
                continue
            return row, col
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 9.")

def main():
    board = [[" " for _ in range(3)] for _ in range(3)]
    current_player = "X"

    print("Welcome to Tic Tac Toe!")
    print("Positions are numbered like this:")
    print(" 1 | 2 | 3 ")
    print("-----------")
    print(" 4 | 5 | 6 ")
    print("-----------")
    print(" 7 | 8 | 9 ")

    while True:
        print_board(board)
        row, col = get_move(board, current_player)
        board[row][col] = current_player

        if check_win(board, current_player):
            print_board(board)
            print(f"🎉 Player {current_player} wins!")
            break

        if check_draw(board):
            print_board(board)
            print("It's a draw!")
            break

        current_player = "O" if current_player == "X" else "X"

if __name__ == "__main__":
    main()