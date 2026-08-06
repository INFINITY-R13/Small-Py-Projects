# Bagels

import random

NUM_DIGITS = 3
MAX_GUESSES = 10


def get_secret_num():
    """Returns a string that is NUM_DIGITS long, made up of unique random digits."""
    numbers = list('0123456789')
    random.shuffle(numbers)
    secret_num = ''.join(numbers[:NUM_DIGITS])
    return secret_num


def get_clues(guess, secret_num):
    """Returns a string with the pico, fermi, bagels clues for a guess and secret number pair."""
    if guess == secret_num:
        return 'You got it!'

    clues = []

    for i in range(len(guess)):
        if guess[i] == secret_num[i]:
            clues.append('Fermi')
        elif guess[i] in secret_num:
            clues.append('Pico')

    if len(clues) == 0:
        return 'Bagels'
    else:
        clues.sort()
        return ' '.join(clues)


if __name__ == '__main__':
    print(f'I am thinking of a {NUM_DIGITS}-digit number with no repeated digits.')
    print('Try to guess what it is. Here are some clues:')
    print('When I say:    That means:')
    print('  Pico         One digit is correct but in the wrong position.')
    print('  Fermi        One digit is correct and in the right position.')
    print('  Bagels       No digit is correct.')

    while True:
        secret_num = get_secret_num()
        print(f'I have thought up a number. You have {MAX_GUESSES} guesses to get it.')

        num_guesses = 1
        while num_guesses <= MAX_GUESSES:
            guess = input(f'Guess #{num_guesses}: ')
            if len(guess) != NUM_DIGITS or not guess.isdigit():
                print(f'Please enter a {NUM_DIGITS}-digit number.')
                continue

            clues = get_clues(guess, secret_num)
            print(clues)
            num_guesses += 1

            if guess == secret_num:
                break
            if num_guesses > MAX_GUESSES:
                print(f'You ran out of guesses. The answer was {secret_num}.')

        play_again = input('Do you want to play again? (yes or no): ')
        if not play_again.lower().startswith('y'):
            break    