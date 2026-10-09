from logic_utils import (
    check_guess,
    get_hint_message,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)


# ---------- Starter tests ----------

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# ---------- Bug: hints were backwards ----------

def test_too_high_hint_tells_player_to_go_lower():
    # A guess of 60 against a secret of 50 is too high, so the hint must say LOWER
    outcome = check_guess(60, 50)
    assert "LOWER" in get_hint_message(outcome)

def test_too_low_hint_tells_player_to_go_higher():
    # A guess of 40 against a secret of 50 is too low, so the hint must say HIGHER
    outcome = check_guess(40, 50)
    assert "HIGHER" in get_hint_message(outcome)


# ---------- Bug: every second guess was compared as text ----------

def test_single_digit_guess_is_too_low_against_two_digit_secret():
    # As text "9" sorts above "50", but as a number 9 is below 50
    assert check_guess(9, 50) == "Too Low"

def test_secret_passed_as_text_is_still_compared_as_a_number():
    # The old app handed the secret over as a string on even attempts
    assert check_guess(9, "50") == "Too Low"
    assert check_guess(100, "50") == "Too High"
    assert check_guess(50, "50") == "Win"


# ---------- Bug: difficulty ranges ----------

def test_each_difficulty_has_its_own_range():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 100)
    assert get_range_for_difficulty("Hard") == (1, 200)

def test_harder_difficulty_has_a_wider_range():
    # Hard used to be 1 to 50, which was easier than Normal
    easy_low, easy_high = get_range_for_difficulty("Easy")
    normal_low, normal_high = get_range_for_difficulty("Normal")
    hard_low, hard_high = get_range_for_difficulty("Hard")
    assert easy_high < normal_high < hard_high

def test_unknown_difficulty_falls_back_to_default_range():
    assert get_range_for_difficulty("Impossible") == (1, 100)


# ---------- Bug: score was inconsistent ----------

def test_win_on_first_guess_scores_full_points():
    # The old formula took 20 points off a first try win
    assert update_score(0, "Win", 1) == 100

def test_win_loses_ten_points_per_earlier_guess():
    # Winning on the third guess means two earlier guesses, so 100 - 20
    assert update_score(0, "Win", 3) == 80

def test_win_is_always_worth_at_least_ten_points():
    # A very late win would go negative without the minimum
    assert update_score(0, "Win", 50) == 10

def test_wrong_guess_costs_the_same_on_odd_and_even_attempts():
    # "Too High" on an even attempt used to add 5 points instead of removing them
    assert update_score(20, "Too High", 1) == 15
    assert update_score(20, "Too High", 2) == 15
    assert update_score(20, "Too Low", 1) == 15
    assert update_score(20, "Too Low", 2) == 15

def test_score_never_drops_below_zero():
    assert update_score(0, "Too Low", 1) == 0
    assert update_score(3, "Too High", 2) == 0


# ---------- Bug: bad input was accepted ----------

def test_valid_guess_is_parsed_to_an_int():
    assert parse_guess("42") == (True, 42, None)

def test_spaces_around_the_guess_are_ignored():
    assert parse_guess("  42  ") == (True, 42, None)

def test_empty_guess_is_rejected():
    assert parse_guess("") == (False, None, "Enter a guess.")
    assert parse_guess("   ") == (False, None, "Enter a guess.")
    assert parse_guess(None) == (False, None, "Enter a guess.")

def test_word_is_rejected():
    assert parse_guess("abc") == (False, None, "That is not a number.")


# ---------- Edge cases: decimals, negatives, very large values ----------

def test_decimal_guess_is_rejected_instead_of_rounded_down():
    # 50.9 used to be cut down to 50, which could win the game by accident
    is_valid_guess, guess_number, error_message = parse_guess("50.9")
    assert is_valid_guess is False
    assert guess_number is None
    assert error_message == "Enter a whole number, not a decimal."

def test_negative_guess_is_rejected_when_out_of_range():
    is_valid_guess, guess_number, error_message = parse_guess("-5", 1, 100)
    assert is_valid_guess is False
    assert guess_number is None
    assert error_message == "Enter a number between 1 and 100."

def test_extremely_large_guess_is_rejected_when_out_of_range():
    is_valid_guess, guess_number, error_message = parse_guess("999999999999999999999", 1, 100)
    assert is_valid_guess is False
    assert guess_number is None
    assert error_message == "Enter a number between 1 and 100."

def test_guess_with_thousands_of_digits_does_not_crash():
    # Python refuses to convert numbers this long, so it must be handled cleanly
    is_valid_guess, guess_number, error_message = parse_guess("9" * 5000, 1, 100)
    assert is_valid_guess is False
    assert guess_number is None

def test_infinity_and_nan_are_not_numbers():
    assert parse_guess("inf") == (False, None, "That is not a number.")
    assert parse_guess("nan") == (False, None, "That is not a number.")

def test_guesses_on_the_edge_of_the_range_are_accepted():
    assert parse_guess("1", 1, 100) == (True, 1, None)
    assert parse_guess("100", 1, 100) == (True, 100, None)

def test_guesses_just_outside_the_range_are_rejected():
    assert parse_guess("0", 1, 100)[0] is False
    assert parse_guess("101", 1, 100)[0] is False
