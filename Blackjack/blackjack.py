
import random
import os
import sys


# Card suits and ranks
SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
VALUES = {
    "A": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
    "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10
}


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def create_deck(num_decks=1):
    """Create and shuffle a deck (or multiple decks)."""
    deck = [(rank, suit) for _ in range(num_decks)
            for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    return deck


def card_str(card):
    """Return a nice string representation of a card."""
    rank, suit = card
    return f"{rank}{suit}"


def hand_str(hand, hide_first=False):
    """Return a string of the hand. Optionally hide the first card (dealer)."""
    if not hand:
        return ""
    if hide_first:
        return f"[??] {' '.join(card_str(c) for c in hand[1:])}"
    return " ".join(card_str(c) for c in hand)


def hand_value(hand):
    """
    Calculate the best total for a hand.
    Aces count as 11 unless that would bust, then as 1.
    """
    total = 0
    aces = 0
    for rank, _ in hand:
        total += VALUES[rank]
        if rank == "A":
            aces += 1
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def is_blackjack(hand):
    """True if the hand is a natural blackjack (Ace + 10-value on first two cards)."""
    return len(hand) == 2 and hand_value(hand) == 21


def deal(deck, hand, n=1):
    """Deal n cards from deck into hand. Returns True if successful."""
    for _ in range(n):
        if not deck:
            return False
        hand.append(deck.pop())
    return True


def print_table(player_hand, dealer_hand, hide_dealer=True, message=""):
    """Display the current game state."""
    clear_screen()
    print("=" * 50)
    print("           ♠ ♥  BLACKJACK  ♦ ♣")
    print("=" * 50)
    print()
    print(f"  Dealer:  {hand_str(dealer_hand, hide_first=hide_dealer)}")
    if not hide_dealer:
        print(f"           Total: {hand_value(dealer_hand)}")
    else:
        # Show only visible card value hint is optional; keep simple
        pass
    print()
    print(f"  You:     {hand_str(player_hand)}")
    print(f"           Total: {hand_value(player_hand)}")
    print()
    if message:
        print(f"  >>> {message}")
        print()
    print("-" * 50)


def get_choice(prompt, valid):
    """Get a valid single-letter choice from the user."""
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid:
            return choice
        print(f"  Please enter one of: {', '.join(valid)}")


def play_round(deck, balance):
    """Play one round of Blackjack. Returns updated balance."""
    player_hand = []
    dealer_hand = []

    # Betting
    print_table([], [], hide_dealer=True)
    print(f"  Your balance: ${balance}")
    while True:
        try:
            bet_str = input("  Enter your bet (or 0 to quit): ").strip()
            bet = int(bet_str)
            if bet == 0:
                return balance, True  # signal quit
            if 1 <= bet <= balance:
                break
            print(f"  Bet must be between $1 and ${balance}.")
        except ValueError:
            print("  Please enter a whole number.")

    # Initial deal: player, dealer, player, dealer
    deal(deck, player_hand)
    deal(deck, dealer_hand)
    deal(deck, player_hand)
    deal(deck, dealer_hand)

    # Check for natural blackjacks
    player_bj = is_blackjack(player_hand)
    dealer_bj = is_blackjack(dealer_hand)

    if player_bj or dealer_bj:
        print_table(player_hand, dealer_hand, hide_dealer=False)
        if player_bj and dealer_bj:
            print("  Both have Blackjack! Push.")
            input("\n  Press Enter to continue...")
            return balance, False
        if player_bj:
            winnings = int(bet * 1.5)
            print(f"  Blackjack! You win ${winnings}!")
            balance += winnings
            input("\n  Press Enter to continue...")
            return balance, False
        # Dealer blackjack
        print("  Dealer has Blackjack. You lose.")
        balance -= bet
        input("\n  Press Enter to continue...")
        return balance, False

    # Player turn
    while True:
        print_table(player_hand, dealer_hand, hide_dealer=True)
        print(f"  Bet: ${bet}   Balance: ${balance}")
        print()
        choice = get_choice("  [H]it  [S]tand  [D]ouble  → ", ["h", "s", "d"])

        if choice == "h":
            if not deal(deck, player_hand):
                print("  Deck empty! Reshuffling...")
                deck.extend(create_deck())
                deal(deck, player_hand)
            if hand_value(player_hand) > 21:
                print_table(player_hand, dealer_hand, hide_dealer=False,
                            message="BUST! You went over 21.")
                balance -= bet
                input("\n  Press Enter to continue...")
                return balance, False

        elif choice == "s":
            break

        elif choice == "d":
            if bet * 2 > balance:
                print("  Not enough balance to double.")
                input("  Press Enter...")
                continue
            if len(player_hand) != 2:
                print("  You can only double on your first two cards.")
                input("  Press Enter...")
                continue
            bet *= 2
            if not deal(deck, player_hand):
                deck.extend(create_deck())
                deal(deck, player_hand)
            if hand_value(player_hand) > 21:
                print_table(player_hand, dealer_hand, hide_dealer=False,
                            message="BUST after doubling!")
                balance -= bet
                input("\n  Press Enter to continue...")
                return balance, False
            break  # after double, stand automatically

    # Dealer turn
    print_table(player_hand, dealer_hand, hide_dealer=False,
                message="Dealer's turn...")
    input("  Press Enter to continue...")

    while hand_value(dealer_hand) < 17:
        if not deal(deck, dealer_hand):
            deck.extend(create_deck())
            deal(deck, dealer_hand)
        print_table(player_hand, dealer_hand, hide_dealer=False,
                    message="Dealer hits...")
        input("  Press Enter...")

    player_total = hand_value(player_hand)
    dealer_total = hand_value(dealer_hand)

    print_table(player_hand, dealer_hand, hide_dealer=False)

    if dealer_total > 21:
        print(f"  Dealer busts with {dealer_total}! You win ${bet}!")
        balance += bet
    elif player_total > dealer_total:
        print(f"  You win! {player_total} beats {dealer_total}. +${bet}")
        balance += bet
    elif player_total < dealer_total:
        print(f"  Dealer wins. {dealer_total} beats {player_total}. -${bet}")
        balance -= bet
    else:
        print(f"  Push! Both have {player_total}.")

    input("\n  Press Enter to continue...")
    return balance, False


def main():
    print("=" * 50)
    print("           ♠ ♥  BLACKJACK  ♦ ♣")
    print("=" * 50)
    print()
    print("  Rules:")
    print("  - Get as close to 21 as possible without going over.")
    print("  - Face cards (J, Q, K) are worth 10. Aces are 1 or 11.")
    print("  - Dealer hits on 16 or less, stands on 17+.")
    print("  - Blackjack (Ace + 10) pays 3:2.")
    print("  - Double down available on your first two cards.")
    print()
    input("  Press Enter to start...")

    balance = 1000
    deck = create_deck(num_decks=2)  # two decks for a bit more realism

    while balance > 0:
        if len(deck) < 20:  # reshuffle when running low
            deck = create_deck(num_decks=2)
            print("\n  (Shuffling a fresh shoe...)")
            input("  Press Enter...")

        balance, quit_game = play_round(deck, balance)
        if quit_game:
            break

        if balance <= 0:
            clear_screen()
            print("\n  You're out of money. Game over!")
            break

    clear_screen()
    print("=" * 50)
    print(f"  Final balance: ${balance}")
    print("  Thanks for playing!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Game interrupted. Bye!")
        sys.exit(0)