import streamlit as st
import pandas as pd
import os
import math

# --- הגדרות ---
BASE_DIR = "mount"
DATA_FILE = os.path.join(BASE_DIR, "contestants.csv")
LOGO_FILENAME = "LOGO.png"
ITEMS_PER_PAGE = 20

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

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
    
    .stButton button { background: linear-gradient(45deg, #FFD700, #FFC000, #E6AC00); color: #020140; font-weight: 700; font-size: 16px; border-radius: 10px; border: none; width: 100%; padding: 0.5rem; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4); transition: all 0.3s ease; }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6); }
    
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    div[data-testid="stImage"] img { border-radius: 15px; } 
    
    div[data-testid="stTextInput"] input { background-color: rgba(255, 255, 255, 0.9) !important; border-radius: 10px; border: none; color: #020140 !important; font-weight: bold; direction: rtl; text-align: right; font-size: 16px; padding: 10px;}
    
    div[role="radiogroup"] { display: flex; justify-content: space-around; background: rgba(0, 0, 0, 0.3); padding: 15px 5px; border-radius: 15px; border: 1px solid rgba(255, 215, 0, 0.3); margin-bottom: 15px;}
    div[role="radiogroup"] label { font-size: 18px !important; color: white !important; font-weight: bold; cursor: pointer; }
    
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- אתחול משתני סשן ---
if 'voted_for' not in st.session_state:
    st.session_state.voted_for = set()
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
if 'search_input' not in st.session_state:
    st.session_state.search_input = ""
if 'last_search' not in st.session_state:
    st.session_state.last_search = ""

# הפונקציה התקנית לניקוי החיפוש
def clear_search():
    st.session_state.search_input = ""
    st.session_state.current_page = 0

if os.path.exists(LOGO_FILENAME):
    st.image(LOGO_FILENAME, use_container_width=True)

st.title("הצבעה למתמודדים ⭐")

df = load_data()

if df.empty:
    st.warning("אין נרשמים עדיין.")
else:
    # --- שורת חיפוש מעוצבת ---
    st.markdown("<p style='text-align: right; color: #FFD700 !important; font-weight: bold; margin-bottom: 5px;'>חפש מתמודד:</p>", unsafe_allow_html=True)
    col_search, col_btn_s, col_btn_c = st.columns([3, 1, 1])
    
    with col_search:
        st.text_input(
            "חיפוש", 
            placeholder="הקלד שם או תחפושת...", 
            key="search_input", 
            label_visibility="collapsed"
        )
        
    with col_btn_s:
        # כפתור שמפעיל רענון כדי לקלוט את החיפוש
        st.button("🔍 חפש", use_container_width=True)
        
    with col_btn_c:
        # שימוש בפונקציית הניקוי
        st.button("✖️ נקה", on_click=clear_search, use_container_width=True)
    
    search_query = st.session_state.search_input
    
    # איפוס עמוד אם החיפוש השתנה
    if search_query != st.session_state.last_search:
        st.session_state.current_page = 0
        st.session_state.last_search = search_query
    
    # ביצוע הסינון בפועל
    if search_query:
        mask_names = df['names'].astype(str).str.contains(search_query, case=False, na=False)
        mask_costume = df['costume_name'].astype(str).str.contains(search_query, case=False, na=False)
        df = df[mask_names | mask_costume]
    
    if df.empty:
        st.info("לא נמצאו מתמודדים התואמים לחיפוש שלך.")
    else:
        # --- חישוב עמודים ---
        total_items = len(df)
        total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
        
        if st.session_state.current_page >= total_pages:
            st.session_state.current_page = max(0, total_pages - 1)
            
        start_idx = st.session_state.current_page * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        current_df = df.iloc[start_idx:end_idx]
        
        # --- ניווט עליון ---
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

        # --- הצגת מתמודדים ---
        for index, row in current_df.iterrows():
            with st.container():
                if pd.notna(row.get("image_path")) and os.path.exists(row["image_path"]):
                    st.image(row["image_path"], use_container_width=True)
                
                st.markdown(f"### {row['names']}")
                st.markdown(f"**קטגוריה:** {row['category']} | 🎭 **{row['costume_name']}**")
                
                contestant_id = row['id']
                if contestant_id in st.session_state.voted_for:
                    st.success("✅ ההצבעה שלך נקלטה בהצלחה!")
                else:
                    st.markdown("<p style='text-align: right; color: #FFD700 !important; font-weight: bold; margin-bottom: 5px;'>איזה ציון מגיע להם? (5 הכי גבוה)</p>", unsafe_allow_html=True)
                    
                    vote_val = st.radio(
                        "ציון:",
                        options=[1, 2, 3, 4, 5],
                        format_func=lambda x: f"{x} ⭐",
                        horizontal=True,
                        key=f"s_{contestant_id}",
                        label_visibility="collapsed"
                    )
                    
                    if st.button("שלח דירוג", key=f"b_{contestant_id}"):
                        original_df = load_data()
                        match_df = original_df[original_df['id'] == contestant_id]
                        
                        if not match_df.empty:
                            orig_index = match_df.index[0]
                            original_df.at[orig_index, "total_score"] += vote_val
                            original_df.at[orig_index, "votes_count"] += 1
                            save_data(original_df)
                            
                            st.session_state.voted_for.add(contestant_id)
                            st.rerun()

        # --- ניווט תחתון ---
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