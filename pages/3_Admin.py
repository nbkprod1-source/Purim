import streamlit as st
import pandas as pd
import os

BASE_DIR = "mount"
DATA_FILE = os.path.join(BASE_DIR, "contestants.csv")
ADMIN_PASSWORD = "300" # סיסמת הגישה לפאנל הניהול

st.set_page_config(page_title="ניהול מערכת", layout="wide")

# עיצוב והסתרת תפריט צדדי
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;700&display=swap" rel="stylesheet">
<style>
    .stApp { font-family: 'Rubik', sans-serif; direction: rtl; text-align: right; }
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

st.title("⚙️ פאנל ניהול - נתוני נרשמים")

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    password = st.text_input("הכנס סיסמת מנהל:", type="password")
    if st.button("כניסה"):
        if password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("סיסמה שגויה")
else:
    if st.button("התנתק"):
        st.session_state.admin_logged_in = False
        st.rerun()
        
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if df.empty:
            st.write("אין נרשמים במערכת כרגע.")
        else:
            st.write(f"**סה\"כ מתמודדים רשומים:** {len(df)}")
            st.dataframe(df, use_container_width=True)
            
            # כפתור הורדה לאקסל
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 הורד את כל הנתונים כקובץ אקסל (CSV)",
                data=csv,
                file_name='contestants_data.csv',
                mime='text/csv',
            )
    else:
        st.write("קובץ הנתונים עדיין לא נוצר (טרם נרשמו מתמודדים).")