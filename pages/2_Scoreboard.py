import streamlit as st
import pandas as pd
import os
import base64

BASE_DIR = "mount"
DATA_FILE = os.path.join(BASE_DIR, "contestants.csv")
LOGO_FILENAME = "LOGO.png"

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

# פונקציה להצגת תמונה בתוך קוד HTML
def get_image_base64(image_path):
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            data = base64.b64encode(img_file.read()).decode("utf-8")
            return f"data:image/jpeg;base64,{data}"
    return ""

st.set_page_config(page_title="לוח תוצאות", layout="wide")

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;700&display=swap" rel="stylesheet">
<style>
    .stApp { background: radial-gradient(circle at 50% -20%, #1a1a60, #020140, #000000); font-family: 'Rubik', sans-serif; direction: rtl; text-align: right; }
    h1, h2, h3 { text-align: center !important; color: white !important; text-shadow: 0 0 10px rgba(255, 255, 255, 0.3); }
    p, .stMarkdown { color: #E0E0E0 !important; text-align: center !important; }
    
    .stButton button { background: linear-gradient(45deg, #FFD700, #FFC000, #E6AC00); color: #020140; font-weight: 700; font-size: 18px; border-radius: 12px; border: none; width: 100%; padding: 0.6rem 1rem; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4); transition: all 0.3s ease; }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6); }
    
    /* עיצוב המקום הראשון */
    .winner-card { background: linear-gradient(135deg, rgba(255, 215, 0, 0.9), rgba(255, 255, 255, 0.9)); padding: 25px; border-radius: 20px; color: #020140; text-align: center; direction: rtl; box-shadow: 0 10px 30px rgba(255, 215, 0, 0.5); animation: glow 2s infinite alternate; margin-bottom: 30px; }
    @keyframes glow { from { box-shadow: 0 0 10px #FFD700; } to { box-shadow: 0 0 25px #FFD700, 0 0 10px white; } }
    
    /* עיצוב מקומות 2-10 */
    .top-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.2); padding: 15px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .top-card img { width: 100%; height: 250px; object-fit: cover; border-radius: 10px; margin-bottom: 10px; }
    .rank-badge { background-color: #FFD700; color: #020140; padding: 5px 15px; border-radius: 20px; font-weight: bold; display: inline-block; margin-bottom: 10px; }
    
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    #MainMenu, footer, header { visibility: hidden; }
/* הסתרת התפריט הצדדי לחלוטין */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

if os.path.exists(LOGO_FILENAME):
    col1, col2, col3 = st.columns([1,2,1])
    with col2: st.image(LOGO_FILENAME, use_container_width=True)

st.title("🏆 לוח התוצאות")

colA, colB, colC = st.columns([1,2,1])
with colB:
    if st.button("🔄 רענן נתונים לייב"): st.rerun()

df = load_data()
if not df.empty:
    sorted_df = df.sort_values(by="total_score", ascending=False)
    
    # חלוקה לטופ 10 ושאר המשתתפים
    top10 = sorted_df.head(10)
    rest_df = sorted_df.iloc[10:]
    
    # --- תצוגת המנצח (מקום 1) ---
    winner = top10.iloc[0]
    if winner['total_score'] > 0:
        st.balloons()
        img_src = get_image_base64(winner['image_path'])
        img_html = f'<img src="{img_src}" style="width:100%; max-width: 400px; border-radius:15px; margin-bottom:15px; box-shadow: 0 5px 15px rgba(0,0,0,0.3);">' if img_src else ''
        
        # חילוץ משתנים בצורה נקייה 
        w_costume = winner['costume_name']
        w_names = winner['names']
        w_cat = winner['category']
        w_score = winner['total_score']
        w_votes = winner['votes_count']
        
        # בניית ה-HTML בצורה בטוחה ללא מרכאות משולשות
        winner_html = (
            '<div class="winner-card">'
            '<h1 style="color: #020140 !important;">🏆 מקום ראשון 🏆</h1>'
            + img_html +
            f'<h2 style="color: #020140 !important;">{w_costume}</h2>'
            f'<h3 style="color: #020140 !important;">{w_names} ({w_cat})</h3>'
            f'<h1 style="color: #020140 !important;">{w_score} נקודות</h1>'
            f'<p style="color: #020140 !important;">({w_votes} הצבעות)</p>'
            '</div>'
        )
        st.markdown(winner_html, unsafe_allow_html=True)
    
    # --- תצוגת עשרת הגדולים (מקומות 2-10) ---
    if len(top10) > 1:
        st.markdown("### 🌟 עשרת הגדולים 🌟")
        cols = st.columns(3) 
        
        for i in range(1, len(top10)):
            row = top10.iloc[i]
            img_src = get_image_base64(row['image_path'])
            img_html = f'<img src="{img_src}">' if img_src else '<div style="height:250px; background:rgba(0,0,0,0.2); border-radius:10px; display:flex; align-items:center; justify-content:center;">אין תמונה</div>'
            
            c_costume = row['costume_name']
            c_names = row['names']
            c_cat = row['category']
            c_score = row['total_score']
            
            # בניית ה-HTML בצורה בטוחה
            card_html = (
                '<div class="top-card">'
                f'<div class="rank-badge">מקום {i+1}</div>'
                + img_html +
                f'<h3 style="color: white; margin: 5px 0;">{c_costume}</h3>'
                f'<p style="color: #E0E0E0; margin: 0;">{c_names} ({c_cat})</p>'
                f'<h4 style="color: #FFD700; margin: 5px 0;">{c_score} נקודות</h4>'
                '</div>'
            )
            with cols[(i-1) % 3]:
                st.markdown(card_html, unsafe_allow_html=True)

    # --- טבלה לשאר המשתתפים (ממקום 11 ומטה) ---
    if not rest_df.empty:
        st.markdown("---")
        st.markdown("### 📊 שאר הדירוגים")
        display = rest_df[["total_score", "votes_count", "category", "costume_name", "names"]]
        display.columns = ["סך נקודות", "מס' מצביעים", "קטגוריה", "תחפושת", "משתתפים"]
        st.dataframe(display, use_container_width=True)
else:
    st.write("אין נתונים עדיין. מחכים לנרשמים הראשונים!")