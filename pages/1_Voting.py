import streamlit as st
import pandas as pd
import os
import math

# --- הגדרות ---
BASE_DIR = "mount"
DATA_FILE = os.path.join(BASE_DIR, "contestants.csv")
LOGO_FILENAME = "LOGO.png"
ITEMS_PER_PAGE = 20 # כאן קובעים כמה מתמודדים יופיעו בכל עמוד

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

def save_data(df): df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="הצבעה לתחפושות", layout="centered")

# --- עיצוב CSS ---
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;700&display=swap" rel="stylesheet">
<style>
    .stApp { background: radial-gradient(circle at 50% -20%, #1a1a60, #020140, #000000); font-family: 'Rubik', sans-serif; direction: rtl; text-align: right; }
    h1, h2, h3 { text-align: center !important; color: white !important; text-shadow: 0 0 10px rgba(255, 255, 255, 0.3); }
    p, .stMarkdown { color: #E0E0E0 !important; text-align: center !important; }
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); padding: 20px; margin-bottom: 20px;}
    .stButton button { background: linear-gradient(45deg, #FFD700, #FFC000, #E6AC00); color: #020140; font-weight: 700; font-size: 18px; border-radius: 12px; border: none; width: 100%; padding: 0.6rem 1rem; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4); transition: all 0.3s ease; }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6); }
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    div[data-testid="stImage"] img { border-radius: 15px; } /* עיגול פינות לתמונות */
    
    #MainMenu, footer, header { visibility: hidden; }
    /* הסתרת התפריט הצדדי לחלוטין */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# משתני סשן (לשמירת ההצבעה והעמוד הנוכחי)
if 'voted_for' not in st.session_state: st.session_state.voted_for = set()
if 'current_page' not in st.session_state: st.session_state.current_page = 0

if os.path.exists(LOGO_FILENAME): st.image(LOGO_FILENAME, use_container_width=True)

st.title("הצבעה למתמודדים ⭐")

df = load_data()
if df.empty:
    st.warning("אין נרשמים עדיין.")
else:
    # --- חישוב עמודים ---
    total_items = len(df)
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
    
    # מונע מצב של חריגה מעמודים קיימים
    if st.session_state.current_page >= total_pages:
        st.session_state.current_page = max(0, total_pages - 1)
        
    start_idx = st.session_state.current_page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_df = df.iloc[start_idx:end_idx] # חיתוך המתמודדים לעמוד הספציפי
    
    # --- כפתורי ניווט (למעלה) ---
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col1:
            if st.button("⬅️ הבא", key="next_top", disabled=(st.session_state.current_page >= total_pages - 1)):
                st.session_state.current_page += 1
                st.rerun()
        with col2:
            st.markdown(f"<h4 style='color: #FFD700 !important; margin-top: 10px;'>עמוד {st.session_state.current_page + 1} מתוך {total_pages}</h4>", unsafe_allow_html=True)
        with col3:
            if st.button("הקודם ➡️", key="prev_top", disabled=(st.session_state.current_page == 0)):
                st.session_state.current_page -= 1
                st.rerun()
        st.markdown("---")

    # --- הצגת המתמודדים בעמוד הנוכחי ---
    for index, row in current_df.iterrows():
        with st.container():
            if pd.notna(row.get("image_path")) and os.path.exists(row["image_path"]):
                st.image(row["image_path"], use_container_width=True)
            
            st.markdown(f"### {row['names']}")
            st.markdown(f"**קטגוריה:** {row['category']} | 🎭 **{row['costume_name']}**")
            
            contestant_id = row['id']
            if contestant_id in st.session_state.voted_for:
                st.success("✅ ההצבעה שלך נקלטה!")
            else:
                vote_val = st.slider("דרג את התחפושת:", 1, 5, value=3, key=f"s_{index}")
                if st.button("שלח דירוג", key=f"b_{index}"):
                    # הוספת הניקוד לקובץ המקורי
                    df.at[index, "total_score"] += vote_val
                    df.at[index, "votes_count"] += 1
                    save_data(df)
                    st.session_state.voted_for.add(contestant_id)
                    st.rerun()

    # --- כפתורי ניווט (למטה) ---
    if total_pages > 1 and len(current_df) > 3:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col1:
            if st.button("⬅️ הבא", key="next_bottom", disabled=(st.session_state.current_page >= total_pages - 1)):
                st.session_state.current_page += 1
                st.rerun()
        with col2:
            st.markdown(f"<h4 style='color: #FFD700 !important; margin-top: 10px;'>עמוד {st.session_state.current_page + 1} מתוך {total_pages}</h4>", unsafe_allow_html=True)
        with col3:
            if st.button("הקודם ➡️", key="prev_bottom", disabled=(st.session_state.current_page == 0)):
                st.session_state.current_page -= 1
                st.rerun()