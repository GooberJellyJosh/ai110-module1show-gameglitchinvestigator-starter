Git Repo Link: https://github.com/GooberJellyJosh/ai110-module1show-gameglitchinvestigator-starter

# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] Describe the game's purpose.
- [x] Detail which bugs you found.
- [x] Explain what fixes you applied.

### The game's purpose

This is a number guessing game built with Streamlit. The game picks a secret number, and the player has a limited number of attempts to find it. After each guess the game says whether to go higher or lower, and the score depends on how quickly the player gets there. The difficulty setting changes both the range of the secret and the number of attempts:

| Difficulty | Range | Attempts |
|------------|-------|----------|
| Easy | 1 to 20 | 6 |
| Normal | 1 to 100 | 8 |
| Hard | 1 to 200 | 5 |

### Bugs found

1. **Backwards hints.** A guess above the secret said "Go HIGHER!" and a guess below it said "Go LOWER!".
2. **Text comparison on every second guess.** On even numbered attempts the secret was turned into a string, so 9 was treated as higher than 50.
3. **One attempt missing.** The attempt counter started at 1, so Normal gave 7 guesses instead of 8.
4. **New Game did not work.** After a win or loss the status never reset, so the game stayed locked, and the score and history carried over.
5. **Difficulty was ignored.** The banner always said "between 1 and 100", New Game always picked from 1 to 100, switching difficulty kept the old secret, and Hard (1 to 50) was easier than Normal.
6. **Inconsistent score.** Some wrong guesses added 5 points, and a win was worth 10 points less than intended.
7. **Bad input was accepted.** Text like `abc` used up an attempt, `50.9` was silently cut down to 50, and out of range numbers were allowed.
8. **Stale "Attempts left" banner.** The banner was drawn before the guess was processed, so it was always one guess behind.

The full reproduction log for these is in [reflection.md](reflection.md).

### Fixes applied

- **Refactor:** `get_range_for_difficulty`, `parse_guess`, `check_guess` and `update_score` moved out of `app.py` into [logic_utils.py](logic_utils.py), so the rules can be tested without starting Streamlit. `app.py` now only handles the page layout and the session state.
- **Hints (bugs 1 and 2):** `check_guess` converts both values to `int` before comparing and returns only the outcome (`"Win"`, `"Too High"` or `"Too Low"`). The new `get_hint_message` turns the outcome into the hint text, with "Too High" pointing the player lower.
- **Attempts (bugs 3 and 8):** attempts start at 0 and only go up for a valid guess. The banner is a placeholder that is filled in after the guess is handled, so it is always up to date.
- **New Game and difficulty (bugs 4 and 5):** a single `start_new_game` function in `app.py` resets the secret, attempts, score, status and history. It runs on the first load, when New Game is clicked, and when the difficulty changes, and it always picks the secret from the selected range. Hard is now 1 to 200.
- **Score (bug 6):** `update_score` takes 5 points off for every wrong guess (never going below 0) and gives `100 - 10 * (earlier guesses)` for a win, with a minimum of 10.
- **Input (bug 7):** `parse_guess` rejects empty input, words, decimals and numbers outside the range, each with its own message, and none of them cost an attempt.
- **Tests:** [tests/test_game_logic.py](tests/test_game_logic.py) keeps the 3 starter tests and adds 23 more that target each bug above plus edge cases (decimals, negatives, very large values). A `pytest.ini` was added so a plain `pytest` command can import `logic_utils`.

## 📸 Demo Walkthrough

A sample game on Normal difficulty (range 1 to 100, 8 attempts) where the secret number is 65:

1. The page loads and the banner reads "Guess a number between 1 and 100. Attempts left: 8". The score is 0.
2. User enters `abc` → the game shows "That is not a number." Attempts left stays at 8.
3. User enters `50.9` → the game shows "Enter a whole number, not a decimal." Attempts left stays at 8.
4. User enters a guess of 80 → the game returns "📉 Go LOWER!" Attempts left drops to 7.
5. User enters a guess of 9 → the game returns "📈 Go HIGHER!" Attempts left drops to 6.
6. User enters a guess of 65 → the game returns "🎉 Correct!" followed by "You won! The secret was 65. Final score: 80" (100 points minus 10 for each of the two earlier guesses).
7. User clicks "Submit Guess" again → the game shows "You already won. Start a new game to play again." and nothing else changes.
8. User clicks "New Game 🔁" → a new secret is picked, the score goes back to 0, the history is cleared, and the banner reads "Attempts left: 8" again.
9. If the user instead uses all 8 attempts without finding the secret, the game shows "Out of attempts! The secret was 65." and locks until New Game is clicked.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

Output of `pytest -v --no-header`:

```
============================= test session starts ==============================
collecting ... collected 26 items

tests/test_game_logic.py::test_winning_guess PASSED                      [  3%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [  7%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 11%]
tests/test_game_logic.py::test_too_high_hint_tells_player_to_go_lower PASSED [ 15%]
tests/test_game_logic.py::test_too_low_hint_tells_player_to_go_higher PASSED [ 19%]
tests/test_game_logic.py::test_single_digit_guess_is_too_low_against_two_digit_secret PASSED [ 23%]
tests/test_game_logic.py::test_secret_passed_as_text_is_still_compared_as_a_number PASSED [ 26%]
tests/test_game_logic.py::test_each_difficulty_has_its_own_range PASSED  [ 30%]
tests/test_game_logic.py::test_harder_difficulty_has_a_wider_range PASSED [ 34%]
tests/test_game_logic.py::test_unknown_difficulty_falls_back_to_default_range PASSED [ 38%]
tests/test_game_logic.py::test_win_on_first_guess_scores_full_points PASSED [ 42%]
tests/test_game_logic.py::test_win_loses_ten_points_per_earlier_guess PASSED [ 46%]
tests/test_game_logic.py::test_win_is_always_worth_at_least_ten_points PASSED [ 50%]
tests/test_game_logic.py::test_wrong_guess_costs_the_same_on_odd_and_even_attempts PASSED [ 53%]
tests/test_game_logic.py::test_score_never_drops_below_zero PASSED       [ 57%]
tests/test_game_logic.py::test_valid_guess_is_parsed_to_an_int PASSED    [ 61%]
tests/test_game_logic.py::test_spaces_around_the_guess_are_ignored PASSED [ 65%]
tests/test_game_logic.py::test_empty_guess_is_rejected PASSED            [ 69%]
tests/test_game_logic.py::test_word_is_rejected PASSED                   [ 73%]
tests/test_game_logic.py::test_decimal_guess_is_rejected_instead_of_rounded_down PASSED [ 76%]
tests/test_game_logic.py::test_negative_guess_is_rejected_when_out_of_range PASSED [ 80%]
tests/test_game_logic.py::test_extremely_large_guess_is_rejected_when_out_of_range PASSED [ 84%]
tests/test_game_logic.py::test_guess_with_thousands_of_digits_does_not_crash PASSED [ 88%]
tests/test_game_logic.py::test_infinity_and_nan_are_not_numbers PASSED   [ 92%]
tests/test_game_logic.py::test_guesses_on_the_edge_of_the_range_are_accepted PASSED [ 96%]
tests/test_game_logic.py::test_guesses_just_outside_the_range_are_rejected PASSED [100%]

============================== 26 passed in 0.03s ==============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
