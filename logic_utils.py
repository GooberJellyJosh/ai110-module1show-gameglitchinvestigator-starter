"""Game rules for the number guessing game.

Nothing in this file touches Streamlit, so every rule can be unit tested
without starting the app.
"""

import math

# Inclusive (low, high) number range for each difficulty.
# FIX: Hard used to be 1 to 50, which was easier than Normal. Each step up in
# difficulty now has a wider range than the one before it.
DIFFICULTY_RANGES = {
    "Easy": (1, 20),
    "Normal": (1, 100),
    "Hard": (1, 200),
}

# Range used when the difficulty name is not recognised.
DEFAULT_RANGE = (1, 100)

# Points for winning on the very first guess.
MAX_WIN_POINTS = 100
# Points taken off the win bonus for each guess made before the winning one.
WIN_POINTS_LOST_PER_GUESS = 10
# A win is always worth at least this much.
MIN_WIN_POINTS = 10
# Points lost for every wrong guess.
WRONG_GUESS_PENALTY = 5

# Hint shown to the player for each outcome of a guess.
HINT_MESSAGES = {
    "Win": "🎉 Correct!",
    "Too High": "📉 Go LOWER!",
    "Too Low": "📈 Go HIGHER!",
}


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    return DIFFICULTY_RANGES.get(difficulty, DEFAULT_RANGE)


def parse_guess(raw: str, low: int = None, high: int = None):
    """
    Parse user input into an int guess.

    When low and high are given, the guess must also fall inside that
    inclusive range.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    # Nothing typed yet (or only spaces).
    if raw is None or raw.strip() == "":
        return False, None, "Enter a guess."

    guess_text = raw.strip()

    try:
        guess_number = int(guess_text)
    except ValueError:
        # FIX: Decimals used to be cut down to a whole number, so 50.9 could win
        # against a secret of 50. They are now rejected with their own message.
        if _is_decimal_number(guess_text):
            return False, None, "Enter a whole number, not a decimal."
        return False, None, "That is not a number."

    # FIX: Guesses outside the range (negative numbers, huge numbers) used to be
    # accepted and cost the player an attempt.
    if low is not None and high is not None:
        if guess_number < low or guess_number > high:
            return False, None, f"Enter a number between {low} and {high}."

    return True, guess_number, None


def _is_decimal_number(text: str):
    """Return True when text is a real number like "50.9" rather than a word."""
    try:
        return math.isfinite(float(text))
    except ValueError:
        return False


def check_guess(guess, secret):
    """
    Compare guess to secret and return the outcome.

    The outcome is one of "Win", "Too High" or "Too Low". Use
    get_hint_message() to turn it into the text shown to the player.
    """
    # FIX: The old version fell back to comparing the two values as text, which
    # sorts "9" above "50". Converting both to int first means the comparison is
    # always numeric, even if the caller passes the secret in as a string.
    guess_number = int(guess)
    secret_number = int(secret)

    if guess_number == secret_number:
        return "Win"
    if guess_number > secret_number:
        return "Too High"
    return "Too Low"


def get_hint_message(outcome: str):
    """Return the hint to show the player for an outcome from check_guess()."""
    # FIX: The two messages used to be swapped, so a guess that was too high told
    # the player to go higher. "Too High" now points the player lower.
    return HINT_MESSAGES[outcome]


def update_score(current_score: int, outcome: str, attempt_number: int):
    """
    Update score based on outcome and attempt number.

    attempt_number is the number of the guess that was just made, starting at 1
    for the first guess of the game.
    """
    if outcome == "Win":
        # FIX: The old formula used (attempt_number + 1), which took points off
        # even for a first try win. Only the guesses made before the winning one
        # reduce the bonus now.
        earlier_guesses = attempt_number - 1
        win_points = MAX_WIN_POINTS - WIN_POINTS_LOST_PER_GUESS * earlier_guesses
        return current_score + max(win_points, MIN_WIN_POINTS)

    if outcome in ("Too High", "Too Low"):
        # FIX: A "Too High" guess on an even attempt used to add 5 points. Every
        # wrong guess now costs the same, and the score never drops below zero.
        return max(current_score - WRONG_GUESS_PENALTY, 0)

    # Unknown outcomes leave the score alone.
    return current_score
