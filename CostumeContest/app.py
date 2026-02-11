import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- הגדרות מערכת ---
BASE_DIR = "mount"
IMAGES_DIR = os.path.join(BASE_DIR, "images")
DATA_FILE = os.path.join(BASE_DIR, "contestants.csv")
LOGO_FILENAME = "LOGO.png"

if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)
if not os.path.exists(IMAGES_DIR): os.makedirs(IMAGES_DIR)

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["id", "timestamp", "category", "names", "contact_name", "phone", "email", "costume_name", "image_path", "total_score", "votes_count"])

def save_data(df): df.to_csv(DATA_FILE, index=False)

def save_image(uploaded_file, email):
    if uploaded_file is not None:
        ext = uploaded_file.name.split(".")[-1]
        filename = f"{email.split('@')[0] if email else 'entry'}_{datetime.now().strftime('%H%M%S')}.{ext}"
        filepath = os.path.join(IMAGES_DIR, filename)
        with open(filepath, "wb") as f: f.write(uploaded_file.getbuffer())
        return filepath
    return None

st.set_page_config(page_title="טופס הרשמה לתחרות", layout="centered")

# --- עיצוב CSS ---
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;700&display=swap" rel="stylesheet">
<style>
    .stApp { background: radial-gradient(circle at 50% -20%, #1a1a60, #020140, #000000); font-family: 'Rubik', sans-serif; direction: rtl; text-align: right; }
    h1, h2, h3, h4 { text-align: center !important; color: white !important; text-shadow: 0 0 10px rgba(255, 255, 255, 0.3); }
    p, .stMarkdown { color: #E0E0E0 !important; text-align: center !important; }
    div[data-testid="stForm"] { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); padding: 20px; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.37); }
    .stTextInput input, .stTextArea textarea { background-color: rgba(255, 255, 255, 0.9) !important; border-radius: 10px; border: none; color: #020140 !important; font-weight: bold; direction: rtl; text-align: right; }
    label, div[data-testid="stCaptionContainer"] { text-align: right !important; direction: rtl !important; color: white !important; width: 100%; }
    div[data-testid="stFileUploader"] { direction: rtl; text-align: right; }
    .stButton button { background: linear-gradient(45deg, #FFD700, #FFC000, #E6AC00); color: #020140; font-weight: 700; font-size: 18px; border-radius: 12px; border: none; width: 100%; padding: 0.6rem 1rem; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4); transition: all 0.3s ease; }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6); }
    div[role="radiogroup"] { display: flex; justify-content: center; gap: 10px; background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 20px; border: 1px solid rgba(255, 215, 0, 0.3); margin-bottom: 20px;}
    div[role="radiogroup"] > label { padding: 5px 15px; cursor: pointer; }
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="collapsedControl"] { display: none; }
</style>
""", unsafe_allow_html=True)

if os.path.exists(LOGO_FILENAME): st.image(LOGO_FILENAME, use_container_width=True)

st.title("הצטרפות לתחרות התחפושות")
st.markdown("#### באיזו קטגוריה אתם מתחרים?")

# הוסר האימוג'י - כעת טקסט נקי בלבד
category = st.radio("בחר קטגוריה", ["יחיד", "זוג", "קבוצה"], horizontal=True, label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

with st.form("entry_form", clear_on_submit=True):
    fname = lname = name1 = name2 = group_names = contact = phone = email = costume = ""
    photo = None

    if category == "יחיד":
        col1, col2 = st.columns(2)
        with col1:
            fname = st.text_input("שם פרטי *")
            lname = st.text_input("שם משפחה *")
            phone = st.text_input("מספר טלפון *")
        with col2:
            email = st.text_input("כתובת Email (לא חובה)")
            costume = st.text_input("שם התחפושת *")
            photo = st.file_uploader("העלה תמונה *", type=['jpg', 'png', 'jpeg'])

    elif category == "זוג":
        col1, col2 = st.columns(2)
        with col1:
            name1 = st.text_input("שם מלא - בן/בת זוג 1 *")
            name2 = st.text_input("שם מלא - בן/בת זוג 2 *")
            contact = st.text_input("שם איש קשר (לזכייה בפרס) *")
        with col2:
            phone = st.text_input("טלפון איש קשר *")
            email = st.text_input("כתובת Email (לא חובה)")
            costume = st.text_input("שם התחפושת *")
        photo = st.file_uploader("העלה תמונה זוגית *", type=['jpg', 'png', 'jpeg'])

    else: # קבוצה
        col1, col2 = st.columns(2)
        with col1:
            group_names = st.text_area("שמות חברי הקבוצה *")
            contact = st.text_input("שם איש קשר (לזכייה בפרס) *")
        with col2:
            phone = st.text_input("טלפון איש קשר *")
            email = st.text_input("כתובת Email (לא חובה)")
            costume = st.text_input("שם התחפושת *")
        photo = st.file_uploader("העלה תמונה קבוצתית *", type=['jpg', 'png', 'jpeg'])

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("שלח והירשם לתחרות")

    if submitted:
        valid = False
        final_names = ""
        final_contact = ""

        if category == "יחיד" and fname and lname and phone and costume and photo:
            valid = True
            final_names = f"{fname} {lname}"
            final_contact = final_names
        elif category == "זוג" and name1 and name2 and contact and phone and costume and photo:
            valid = True
            final_names = f"{name1} ו-{name2}"
            final_contact = contact
        elif category == "קבוצה" and group_names and contact and phone and costume and photo:
            valid = True
            final_names = group_names.replace('\n', ', ')
            final_contact = contact

        if valid:
            saved_path = save_image(photo, email if email else phone)
            df = load_data()
            new_entry = {
                "id": len(df) + 1, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "category": category, "names": final_names, "contact_name": final_contact,
                "phone": phone, "email": email, "costume_name": costume, 
                "image_path": saved_path, "total_score": 0, "votes_count": 0
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(df)
            st.success(f"איזה יופי! נרשמתם כ{category}. בהצלחה בתחרות!")
        else:
            st.error("נא למלא את כל שדות החובה המסומנים בכוכבית (*)")