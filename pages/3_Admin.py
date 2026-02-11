import streamlit as st
import pandas as pd
import os
import io
import zipfile

BASE_DIR = "mount"
DATA_FILE = os.path.join(BASE_DIR, "contestants.csv")
ADMIN_PASSWORD = "1122334455" # הסיסמה החדשה

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
    
    /* עיצוב כפתורי ההורדה */
    .stDownloadButton button { background: linear-gradient(45deg, #FFD700, #FFC000); color: #020140; font-weight: bold; border-radius: 10px; border: none; }
    .stDownloadButton button:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(255, 215, 0, 0.4); }
</style>
""", unsafe_allow_html=True)

st.title("⚙️ פאנל ניהול - נתוני נרשמים")

# ניהול התחברות
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
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("התנתק"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if df.empty:
            st.warning("אין נרשמים במערכת כרגע.")
        else:
            st.markdown(f"### סה\"כ מתמודדים רשומים: **{len(df)}**")
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- אזור הורדת הנתונים ---
            c1, c2 = st.columns(2)
            
            with c1:
                # כפתור הורדה לאקסל
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 הורד את כל הנתונים כקובץ אקסל (CSV)",
                    data=csv,
                    file_name='contestants_data.csv',
                    mime='text/csv',
                    use_container_width=True
                )
                
            with c2:
                # יצירת קובץ ZIP של כל התמונות
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for _, row in df.iterrows():
                        img_path = row.get('image_path')
                        if pd.notna(img_path) and os.path.exists(str(img_path)):
                            ext = os.path.splitext(img_path)[1]
                            
                            # ניקוי השם מתווים שאסורים בשמות של קבצים (כמו לוכסנים או גרשיים)
                            contact_name = str(row.get('contact_name', row.get('names', 'Unknown')))
                            clean_name = contact_name.replace("/", "-").replace("\\", "-").replace('"', '').replace("'", "").replace(":", "")
                            
                            # הוספת ה-ID לשם הקובץ כדי למנוע דריסה אם לשני משתתפים יש אותו שם
                            filename = f"{clean_name}_{row['id']}{ext}"
                            zip_file.write(img_path, arcname=filename)
                
                st.download_button(
                    label="📸 הורד את כל התמונות (קובץ ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name='Costumes_Images.zip',
                    mime='application/zip',
                    use_container_width=True
                )
            
            st.markdown("<br><hr>", unsafe_allow_html=True)
            st.markdown("### 📋 רשימת מתמודדים ומחיקה")
            
            # --- טבלת ניהול דינמית עם כפתורי מחיקה ---
            # כותרות הטבלה
            col_id, col_name, col_costume, col_cat, col_score, col_del = st.columns([1, 3, 3, 2, 2, 2])
            col_id.markdown("**ID**")
            col_name.markdown("**שם המשתתף/ת**")
            col_costume.markdown("**תחפושת**")
            col_cat.markdown("**קטגוריה**")
            col_score.markdown("**ניקוד**")
            col_del.markdown("**פעולה**")
            
            st.markdown("<hr style='margin: 0; padding: 0;'>", unsafe_allow_html=True)
            
            # הדפסת השורות
            for index, row in df.iterrows():
                c_id, c_name, c_costume, c_cat, c_score, c_del = st.columns([1, 3, 3, 2, 2, 2])
                c_id.write(row['id'])
                c_name.write(row['names'])
                c_costume.write(row['costume_name'])
                c_cat.write(row['category'])
                c_score.write(f"{row['total_score']} ({row['votes_count']} קולות)")
                
                with c_del:
                    # יצירת כפתור מחיקה ייחודי לכל שורה
                    if st.button("🗑️ מחק", key=f"del_{row['id']}"):
                        
                        # מחיקת התמונה מהכונן בשרת
                        if pd.notna(row['image_path']) and os.path.exists(row['image_path']):
                            try:
                                os.remove(row['image_path'])
                            except:
                                pass # אם התמונה כבר לא קיימת, תתעלם ותמשיך
                                
                        # מחיקת השורה מהטבלה ושמירה
                        df = df[df['id'] != row['id']]
                        df.to_csv(DATA_FILE, index=False)
                        
                        st.success("המתמודד נמחק בהצלחה!")
                        st.rerun() # רענון הדף כדי להציג את הרשימה המעודכנת
                        
                st.markdown("<hr style='margin: 0; padding: 0; opacity: 0.2;'>", unsafe_allow_html=True)

    else:
        st.warning("קובץ הנתונים עדיין לא נוצר (טרם נרשמו מתמודדים).")