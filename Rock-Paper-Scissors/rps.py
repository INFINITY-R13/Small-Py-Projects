import random

def get_computer_choice():
    return random.choice(["rock", "paper", "scissors"])

def determine_winner(player, computer):
    if player == computer:
        return "It's a tie!"
    
    wins = {
        "rock": "scissors",
        "paper": "rock",
        "scissors": "paper"
    }
    
    if wins[player] == computer:
        return "You win!"
    else:
        return "Computer wins!"

def play():
    print("=== Rock Paper Scissors ===")
    print("Type 'rock', 'paper', or 'scissors' (or 'quit' to exit)\n")
    
    while True:
        player = input("Your choice: ").lower().strip()
        
        if player == "quit":
            print("Thanks for playing!")
            break
        
        if player not in ["rock", "paper", "scissors"]:
            print("Invalid choice. Please try again.\n")
            continue
        
        computer = get_computer_choice()
        print(f"Computer chose: {computer}")
        
        result = determine_winner(player, computer)
        print(result + "\n")

if __name__ == "__main__":
    play()