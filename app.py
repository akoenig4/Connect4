import firebase_admin
from firebase_admin import credentials, firestore
import json
import streamlit as st
from c4_gameLogic import (
    is_valid_location, game_is_won, get_valid_locations, create, makeMove,
    isHumTurn, isComputerTurn,
)
from c4_constants import ROW_COUNT, COLUMN_COUNT, RED_INT, BLUE_INT, HUMAN, COMPUTER
import c4_alphaBetaPruning as abp
import time


# -------------------- DATABASE SETUP --------------------


if not firebase_admin._apps:
    firebase_key = json.loads(st.secrets["FIREBASE_KEY"])
    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred)

db = firestore.client()
record_ref = db.collection("connect4").document("record")

db = firestore.client()
record_ref = db.collection("connect4").document("record")

def load_record():
    doc = record_ref.get()
    if not doc.exists:
        record_ref.set({"Player Wins": 0, "AI Wins": 0, "Draws": 0})
        return {"Player Wins": 0, "AI Wins": 0, "Draws": 0}
    return doc.to_dict()

def save_record(record):
    record_ref.set(record)

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Connect 4 AI", layout="centered")

# -------------------- SAFELY INITIALIZE STATE --------------------
if "record" not in st.session_state:
    st.session_state["record"] = load_record()
if "state" not in st.session_state:
    st.session_state["state"] = None
if "game_over" not in st.session_state:
    st.session_state["game_over"] = False
if "winner" not in st.session_state:
    st.session_state["winner"] = None
if "search_depth" not in st.session_state:
    st.session_state["search_depth"] = 4

record = st.session_state["record"]
st.session_state["search_depth"] = 5

# -------------------- STYLES --------------------
st.markdown("""
<style>
.record-box {
    position: fixed;
    top: 1.5rem;
    right: 1.5rem;
    background-color: rgba(25, 55, 109, 0.9);
    color: white;
    border-radius: 15px;
    padding: 1.2rem 1.5rem;
    width: 200px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    font-size: 1rem;
    font-family: "Segoe UI", sans-serif;
    z-index: 9999;
}
.record-box h4 {
    margin-top: 0;
    margin-bottom: 0.75rem;
    text-align: center;
    color: #ffd54f;
    font-weight: 700;
}
.record-box b {
    color: #fff;
}
</style>
""", unsafe_allow_html=True)

# -------------------- STYLE TWEAKS FOR BUTTON SIZE --------------------
st.markdown("""
<style>
div[data-testid="stButton"] > button {
    padding: 0.25rem 0.25rem !important;  /* narrower padding */
    font-size: 0.75rem !important;        /* smaller text */
    border-radius: 8px !important;       /* slightly rounded */
    width: 100% !important;
    height: auto !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------- FLOATING RECORD BOX --------------------
st.markdown(f"""
<div class="record-box">
  <h4>🏆 Record</h4>
  🔴 Player: <b>{record['Player Wins']}</b><br>
  🔵 AI: <b>{record['AI Wins']}</b><br>
  🤝 Draws: <b>{record['Draws']}</b>
</div>
""", unsafe_allow_html=True)

# -------------------- TITLE --------------------
st.title("🔵🔴 Connect 4 vs AI")
st.markdown("---")

# -------------------- ASK WHO GOES FIRST --------------------
if st.session_state.state is None:
    st.session_state.first_choice = st.radio(
        "Who should go first?",
        ("You (Red 🔴)", "Computer (Blue 🔵)")
    )

    if st.button("Start Game"):
        st.session_state.state = create()
        if st.session_state.first_choice == "Computer (Blue 🔵)":
            st.session_state.state[2] = COMPUTER
        else:
            st.session_state.state[2] = HUMAN
        st.session_state.game_over = False
        st.session_state.winner = None
        st.session_state.search_depth = 4
        st.rerun()
    else:
        st.stop()

# -------------------- DISPLAY FUNCTIONS --------------------
def display_board(board):
    st.write("**Column Numbers:**")
    cols = st.columns(7)
    for i, col in enumerate(cols):
        col.write(f"**{i+1}**")

    for r in reversed(range(ROW_COUNT)):
        cols = st.columns(7)
        for c in range(COLUMN_COUNT):
            with cols[c]:
                cell = board[r][c]
                if cell == 0:
                    st.write("⚪")
                elif cell == RED_INT:
                    st.write("🔴")
                elif cell == BLUE_INT:
                    st.write("🔵")

def game_status():
    """Check and display game result"""
    state = st.session_state.state
    board = state[0]

    if game_is_won(board, BLUE_INT):
        st.success("🔵 **AI Wins!** Well played!", icon="✅")
        st.session_state.game_over = True
        return True

    if game_is_won(board, RED_INT):
        st.success("🔴 **You Win!** Congratulations!", icon="🎉")
        st.session_state.game_over = True
        return True

    if len(get_valid_locations(board)) == 0:
        st.info("**Draw!** The board is full.", icon="🤝")
        st.session_state.game_over = True
        return True

    return False

# -------------------- MAIN GAME DISPLAY --------------------
board = st.session_state.state[0]
display_board(board)
st.markdown("---")

# -------------------- GAME LOOP --------------------
if game_status():
    if st.button("Play Again"):
        for key in ['state', 'game_over', 'winner']:  # Remove 'first_choice'
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
else:
    if isHumTurn(st.session_state.state) and not st.session_state.game_over:
        st.write("**Your turn (Red 🔴)**")
        cols = st.columns(7)
        for i, col in enumerate(cols):
            with col:
                if st.button(f"⬇️ {i+1}", key=f"col_{i}", use_container_width=True):
                    if is_valid_location(board, i):
                        makeMove(st.session_state.state, i)
                        # Check game status and update record HERE
                        if game_is_won(st.session_state.state[0], RED_INT):
                            st.session_state.record["Player Wins"] += 1
                            save_record(st.session_state["record"])
                            st.session_state.game_over = True
                        elif game_is_won(st.session_state.state[0], BLUE_INT):
                            st.session_state.record["AI Wins"] += 1
                            save_record(st.session_state["record"])
                            st.session_state.game_over = True
                        elif len(get_valid_locations(st.session_state.state[0])) == 0:
                            st.session_state.record["Draws"] += 1
                            save_record(st.session_state["record"])
                            st.session_state.game_over = True
                        st.rerun()
                    else:
                        st.error("Column full!")

    elif isComputerTurn(st.session_state.state) and not st.session_state.game_over:
        st.write("**AI is thinking... 🤖**")
        start = time.time()
        st.session_state.state, col = abp.go(st.session_state.state, st.session_state.search_depth)
        end = time.time()
        # Check game status and update record HERE
        if game_is_won(st.session_state.state[0], BLUE_INT):
            st.session_state.record["AI Wins"] += 1
            save_record(st.session_state["record"])
            st.session_state.game_over = True
        elif game_is_won(st.session_state.state[0], RED_INT):
            st.session_state.record["Player Wins"] += 1
            save_record(st.session_state["record"])
            st.session_state.game_over = True
        elif len(get_valid_locations(st.session_state.state[0])) == 0:
            st.session_state.record["Draws"] += 1
            save_record(st.session_state["record"])
            st.session_state.game_over = True
        st.write(f"AI played in column **{col+1}** ({end-start:.2f}s)")
        st.rerun()

st.markdown("---")

st.caption("Built with Streamlit | Connect 4 AI using Alpha-Beta Pruning")