import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- הגדרות תיקיית מידע (חשוב לענן!) ---
# כל המידע יישמר בתוך תיקייה בשם "mount"
BASE_DIR = "mount"
IMAGES_DIR = os.path.join(BASE_DIR, "images")
DATA_FILE = os.path.join(BASE_DIR, "contestants.csv")

# סיסמאות
JUDGE_PASSWORD = "100"
SCOREBOARD_PASSWORD = "200"
LOGO_FILENAME = "LOGO.png"

# יצירת התיקיות אם לא קיימות
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# --- פונקציות עזר ---
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "id", "timestamp", "first_name", "last_name", 
            "phone", "email", "costume_name", "image_path", 
            "total_score", "votes_count"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def save_image(uploaded_file, email):
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1]
        filename = f"{email.split('@')[0]}_{datetime.now().strftime('%H%M%S')}.{file_extension}"
        # שמירה בתיקייה הייעודית
        filepath = os.path.join(IMAGES_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        # החזרת נתיב יחסי כדי שהדפדפן ידע לקרוא אותו
        return filepath
    return None

# --- הגדרות עמוד ---
st.set_page_config(page_title="תחרות התחפושות", layout="centered")

# --- עיצוב CSS ---
st.markdown("""
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
        background-color: #020140;
        color: white;
    }
    h1, h2, h3, h4, h5, h6, p, .stMarkdown {
        text-align: center !important;
        color: white !important;
    }
    label, .stRadio label, div[data-testid="stCaptionContainer"] {
        text-align: right !important;
        direction: rtl !important;
        color: white !important;
        width: 100%;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox div, .stNumberInput input {
        direction: rtl;
        text-align: right;
        color: black !important;
    }
    div[data-testid="stFileUploader"] {
        direction: rtl;
        text-align: right;
    }
    .stButton button {
        background-color: #FFD700;
        color: #020140;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        width: 100%;
    }
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 5rem !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- ניהול מצב ---
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'voted_for' not in st.session_state:
    st.session_state.voted_for = set()

def go_home():
    st.session_state.page = "home"
    st.rerun()

# --- לוגו ---
if os.path.exists(LOGO_FILENAME):
    st.image(LOGO_FILENAME, use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

# ===========================
#        תוכן העמודים
# ===========================

# --- עמוד 1: דף הבית (רישום) ---
if st.session_state.page == "home":
    st.title("הצטרפות לתחרות התחפושות")
    st.markdown("### מלאו פרטים והעלו תמונה כדי להשתתף!")
    
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fname = st.text_input("שם פרטי")
            lname = st.text_input("שם משפחה")
            phone = st.text_input("מספר טלפון")
        with col2:
            email = st.text_input("כתובת Email")
            costume = st.text_input("שם התחפושת")
            photo = st.file_uploader("העלה תמונה", type=['jpg', 'png', 'jpeg'])

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("הרשמה לתחרות")

        if submitted:
            if fname and lname and email and costume and photo:
                saved_path = save_image(photo, email)
                df = load_data()
                new_entry = {
                    "id": len(df) + 1,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "first_name": fname,
                    "last_name": lname,
                    "phone": phone,
                    "email": email,
                    "costume_name": costume,
                    "image_path": saved_path,
                    "total_score": 0,
                    "votes_count": 0
                }
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(df)
                st.success("נרשמת בהצלחה! בהצלחה בתחרות!")
            else:
                st.error("נא למלא את כל שדות החובה")

    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("🔐 כניסת שופטים / הצבעת קהל"):
        password = st.text_input("הכנס קוד גישה", type="password")
        if st.button("כנס למערכת"):
            if password == JUDGE_PASSWORD:
                st.session_state.page = "judging"
                st.rerun()
            elif password == SCOREBOARD_PASSWORD:
                st.session_state.page = "scoreboard"
                st.rerun()
            else:
                st.error("קוד שגוי")

# --- עמוד 2: שיפוט ---
elif st.session_state.page == "judging":
    st.title("הצבעה למתמודדים ⭐")
    if st.button("יציאה"):
        go_home()

    df = load_data()
    if df.empty:
        st.warning("אין נרשמים עדיין.")
    else:
        for index, row in df.iterrows():
            with st.container():
                st.markdown("---")
                if row["image_path"] and os.path.exists(row["image_path"]):
                    st.image(row["image_path"], use_container_width=True)
                
                st.markdown(f"### {row['first_name']} {row['last_name']}")
                st.markdown(f"🎭 **{row['costume_name']}**")
                
                contestant_id = row['id']
                
                if contestant_id in st.session_state.voted_for:
                    st.success("✅ ההצבעה שלך נקלטה!")
                else:
                    vote_val = st.slider("דרג את התחפושת:", 1, 5, value=3, key=f"s_{index}")
                    if st.button("שלח דירוג", key=f"b_{index}"):
                        df.at[index, "total_score"] += vote_val
                        df.at[index, "votes_count"] += 1
                        save_data(df)
                        st.session_state.voted_for.add(contestant_id)
                        st.rerun()

# --- עמוד 3: לוח תוצאות ---
elif st.session_state.page == "scoreboard":
    st.title("🏆 לוח התוצאות")
    if st.button("יציאה"):
        go_home()
            
    if st.button("🔄 רענן נתונים"):
        st.rerun()

    df = load_data()
    if not df.empty:
        sorted_df = df.sort_values(by="total_score", ascending=False)
        display = sorted_df[["total_score", "votes_count", "costume_name", "first_name", "last_name"]]
        display.columns = ["סך נקודות", "מס' מצביעים", "תחפושת", "שם פרטי", "שם משפחה"]
        
        winner = sorted_df.iloc[0]
        if winner['total_score'] > 0:
            st.balloons()
            winner_html = f"""
            <div style="background-color: #FFD700; padding: 20px; border-radius: 10px; color: black; text-align: center; direction: rtl;">
                <h1>🏆 מקום ראשון 🏆</h1>
                <h2>{winner['costume_name']}</h2>
                <h3>{winner['first_name']} {winner['last_name']}</h3>
                <h1>{winner['total_score']} נקודות</h1>
                <p>({winner['votes_count']} הצבעות)</p>
            </div>
            <br>
            """
            st.markdown(winner_html, unsafe_allow_html=True)
        
        st.dataframe(display, use_container_width=True)
    else:
        st.write("אין נתונים.")