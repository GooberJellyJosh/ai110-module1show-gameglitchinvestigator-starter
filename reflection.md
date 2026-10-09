# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

The first time I ran it the game looked finished: a title, a difficulty picker in the sidebar, a text box, and Submit / New Game buttons. It only fell apart once I started playing with the "Developer Debug Info" panel open so I could see the secret number. On Normal the banner said "Attempts left: 7" before I had guessed anything, even though the sidebar said 8 attempts were allowed. With the secret at 50, guessing 60 told me to go HIGHER and guessing 40 told me to go LOWER, so following the hints moved me away from the answer. After I finally won, clicking New Game picked a new secret but the page still said "You already won", so the only way to play again was to refresh the browser.

Bugs I found, expected versus actual:

1. **Hints are backwards.** I expected a guess above the secret to say "go lower". It says "Go HIGHER!", and a guess below the secret says "Go LOWER!".
2. **Every second guess is compared as text.** I expected 9 to be "too low" against a secret of 50. On even numbered attempts the game treats it as too high, because the secret is turned into a string and "9" sorts after "50" alphabetically.
3. **The attempt counter starts at 1 instead of 0.** I expected 8 guesses on Normal. The banner starts at 7 and the game ends after my 7th guess.
4. **New Game does not start a new game.** I expected a fresh round after a win or loss. The status stays "won"/"lost", and the score and guess history carry over, so the game stays locked.
5. **Difficulty does not control the range.** I expected the secret and the instructions to follow the selected difficulty. The banner always says "between 1 and 100", New Game always picks from 1 to 100, switching difficulty keeps the old secret, and Hard (1 to 50) is a smaller range than Normal (1 to 100).
6. **The score is inconsistent.** I expected every wrong guess to cost the same. A "too high" guess on an even attempt adds 5 points while every other wrong guess subtracts 5, and a win is worth 10 points less than it should be.
7. **Bad input is handled badly.** I expected "abc" to be rejected without costing me a turn, and 50.9 to be rejected as not a whole number. "abc" uses up an attempt and is added to the history, 50.9 is silently cut down to 50 (and wins), and out of range guesses like -5 or 500 are accepted.
8. **The "Attempts left" banner lags behind.** I expected it to drop right after a guess. It only updates on the next interaction, because the banner is drawn before the guess is processed.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

All rows are on Normal difficulty with the secret at 50 (read from the Developer Debug Info panel) unless the row says otherwise.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Open the app, no guess yet | Banner shows "Attempts left: 8" to match the sidebar | Banner shows "Attempts left: 7" | none |
| Guess of 60 (first guess) | "Too high, go lower" hint, score goes down | "📈 Go HIGHER!" hint, score goes up to 5 | none |
| Guess of 40 (second guess) | "Too low, go higher" hint | "📉 Go LOWER!" hint | none |
| Guess of 9 (third guess, attempt counter is even) | Treated as too low | Treated as too high ("📈 Go HIGHER!"), score goes up by 5 | none (the `TypeError` from comparing an int to a str is caught inside `check_guess`) |
| Guess of `abc` | "That is not a number." and no attempt used | Error is shown, but "Attempts left" drops by one and `abc` is added to the history | none |
| Guess of 50.9 | Rejected, because it is not a whole number | Cut down to 50 and counted as a win: "You won! The secret was 50." | none |
| Guess of 1, seven times in a row | Game over after the 8th wrong guess | "Out of attempts! The secret was 50. Score: -35" after the 7th guess | none |
| Win, then click "New Game 🔁" | New round: status, score, history and attempts all reset | New secret is picked, but the page still says "You already won. Start a new game to play again." and the score stays at 35 | none |
| Switch difficulty from Normal to Easy (range 1 to 20) | New secret between 1 and 20, banner says "between 1 and 20" | Secret stays at 84 and the banner still says "Guess a number between 1 and 100" | none |
| `pytest` on the starter repo | The 3 starter tests pass | 3 failed | `NotImplementedError: Refactor this function from app.py into logic_utils.py` |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.

I only counted a bug as fixed after seeing it pass in two places: a pytest case and the running game. Each bug in the reproduction log got a test that uses the same input that failed before the fix, so the test would have failed against the starter code. After that I replayed the same input in the app with the Developer Debug Info panel open, so I could compare the hint, the attempts left and the score against the secret.

One example is `test_single_digit_guess_is_too_low_against_two_digit_secret`, which checks that `check_guess(9, 50)` returns `"Too Low"`. The old code compared the two values as text on every second attempt and decided 9 was higher than 50. A second test passes the secret in as the string `"50"` to prove the comparison stays numeric either way. In the app, guessing 80 then 9 against a secret of 65 gave "Go LOWER!" then "Go HIGHER!", the banner dropped from 8 to 7 to 6 straight away, and winning on the third guess scored 80.

Testing also showed me two things I was not looking for. The starter tests compare the result of `check_guess` to a single string like `"Win"`, but the original function returned an outcome and a message together, so I made `check_guess` return only the outcome and moved the hint text into `get_hint_message`. Running a plain `pytest` command failed with `ModuleNotFoundError: No module named 'logic_utils'` even though `python -m pytest` worked, which I fixed by adding a `pytest.ini` that puts the project folder on the import path. Playing the fixed game also caught something the tests could not: after I moved the debug panel below the messages, it snapped shut on every guess, so I put the messages in a fixed container to keep the panel in place.

- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

Every time you click a button, type in a box or change a dropdown, Streamlit runs the whole script again from the first line to the last. Any normal variable is created from scratch on each run, so a line like `secret = random.randint(1, 100)` would pick a new secret on every click. `st.session_state` is a dictionary that survives those reruns for one browser tab, so it is the place for anything the game has to remember: the secret, the attempts, the score, the status and the guess history. That is why the app only creates the secret when it is not already in the session state.

The rerun order also explains two of the bugs. The page is drawn in the order the code runs, so the old "Attempts left" banner showed the count from before the guess, because it was drawn above the code that handled the guess. The fix was to reserve the banner's spot with `st.empty()` and fill it in at the end of the script. The New Game bug was the other side of the same idea: session state keeps everything until you change it, so resetting only the attempts and the secret left the old `"won"` status in place and the game stayed locked.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
