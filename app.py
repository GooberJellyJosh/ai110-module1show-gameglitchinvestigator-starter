import random

import streamlit as st

# FIX: The game rules used to be defined in this file, mixed in with the page
# layout. They now live in logic_utils.py so they can be tested with pytest.
from logic_utils import (
    check_guess,
    get_hint_message,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)

# Number of guesses the player gets on each difficulty.
ATTEMPT_LIMITS = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}


def start_new_game(difficulty: str, low: int, high: int):
    """Reset everything stored in the session so a fresh round can begin."""
    # FIX: New Game used to reset only the attempts and the secret. The status
    # stayed "won" or "lost", so the game was locked until the page was refreshed.
    # The secret also ignored the difficulty and was always picked from 1 to 100.
    st.session_state.difficulty = difficulty
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []


# ---------- Page header ----------

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("Guess the secret number before you run out of attempts.")

# ---------- Sidebar settings ----------

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit = ATTEMPT_LIMITS[difficulty]
low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# ---------- Game state ----------

# Streamlit reruns this whole script on every click, so the game is only set up
# when there is no game stored in the session yet.
# FIX: Switching difficulty used to keep the old secret, which could be outside
# the new range. A change of difficulty now starts a new game as well.
is_first_run = "secret" not in st.session_state
difficulty_changed = st.session_state.get("difficulty") != difficulty

if is_first_run or difficulty_changed:
    # FIX: Attempts used to start at 1 here, which cost the player a guess before
    # they had made one. start_new_game() starts the count at 0.
    start_new_game(difficulty, low, high)

# ---------- Guess input ----------

st.subheader("Make a guess")

# FIX: The banner used to be drawn here, before the guess was processed, so
# "Attempts left" was always one guess behind. This placeholder keeps its spot
# on the page and is filled in further down once the guess has been handled.
attempts_banner = st.empty()

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

submit_column, new_game_column, hint_column = st.columns(3)
with submit_column:
    submit_clicked = st.button("Submit Guess 🚀")
with new_game_column:
    new_game_clicked = st.button("New Game 🔁")
with hint_column:
    show_hint = st.checkbox("Show hint", value=True)

# ---------- New game ----------

if new_game_clicked:
    start_new_game(difficulty, low, high)
    # Rerun so the page is redrawn from the top with the fresh game.
    st.rerun()

# ---------- Handle the guess ----------

# Every message about the guess is drawn inside this one container. The
# container is always on the page, so the debug panel below it keeps its place
# (and stays open) whether or not there is a message to show.
feedback_area = st.container()

with feedback_area:
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    elif st.session_state.status == "lost":
        st.error("Game over. Start a new game to try again.")
    elif submit_clicked:
        is_valid_guess, guess_number, error_message = parse_guess(raw_guess, low, high)

        if not is_valid_guess:
            # FIX: Invalid input used to use up an attempt and was saved in the
            # history. Now it only shows the error and the player can try again.
            st.error(error_message)
        else:
            st.session_state.attempts += 1
            st.session_state.history.append(guess_number)

            # FIX: The secret used to be turned into a string on every second
            # attempt, which made the hints wrong. It is always compared as a number.
            outcome = check_guess(guess_number, st.session_state.secret)

            if show_hint:
                st.warning(get_hint_message(outcome))

            st.session_state.score = update_score(
                current_score=st.session_state.score,
                outcome=outcome,
                attempt_number=st.session_state.attempts,
            )

            if outcome == "Win":
                st.balloons()
                st.session_state.status = "won"
                st.success(
                    f"You won! The secret was {st.session_state.secret}. "
                    f"Final score: {st.session_state.score}"
                )
            elif st.session_state.attempts >= attempt_limit:
                # That was the last guess the player was allowed.
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

# ---------- Status banner and debug panel ----------

# These are drawn last so they always show the result of the latest guess.
attempts_left = attempt_limit - st.session_state.attempts

# FIX: The range in this message used to be hard coded as "1 and 100".
attempts_banner.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempts_left}"
)

st.divider()

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)
