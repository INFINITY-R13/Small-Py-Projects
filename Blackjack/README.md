# Blackjack

A complete single-player Blackjack game written in Python. Play against the dealer in your terminal.

## Requirements

- Python 3.6 or higher
- No external packages needed (uses only the standard library)

## How to Run

```bash
python3 blackjack.py
```

## Rules

- Goal: Get as close to **21** as possible without going over.
- Number cards are worth their face value.
- Face cards (**J**, **Q**, **K**) are worth **10**.
- Aces are worth **11** or **1** (whichever is better for the hand).
- Dealer must hit on 16 or less and stand on 17 or more.
- A natural **Blackjack** (Ace + 10-value card on the first two cards) pays **3:2**.
- You may **double down** only on your first two cards (doubles the bet and takes exactly one more card).

## Controls

| Input | Action              |
|-------|---------------------|
| `H`   | Hit (take a card)   |
| `S`   | Stand (end turn)    |
| `D`   | Double down         |
| `0`   | Quit (when betting) |

## Gameplay

1. You start with **$1000**.
2. Place a bet each round (whole dollars only).
3. You and the dealer each receive two cards. The dealer’s first card is hidden.
4. Play your hand (hit / stand / double).
5. Dealer reveals and plays according to the rules.
6. Closest to 21 without busting wins. Ties are a push (bet returned).

The shoe uses two decks and automatically reshuffles when cards run low.

## Files

| File          | Description                |
|---------------|----------------------------|
| `blackjack.py`| Main game script           |
| `README.md`   | This file                  |

## License

Free to use and modify for personal or educational purposes.
