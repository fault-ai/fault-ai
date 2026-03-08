import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text
from fuzzywuzzy import fuzz

# --- ΡΥΘΜΙΣΗ ΑΣΦΑΛΕΙΑΣ ---
# Άλλαξε το "1234" με τον κωδικό που επιθυμείς
PASSWORD = "ΕΕΣΣΤΥ112013$" 

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.set_page_config(page_title="Είσοδος - Fault AI", page_icon="🔒")
    st.title("🔒 Είσοδος στο Σύστημα")
    
    pwd = st.text_input("Εισάγετε τον κωδικό πρόσβασης:", type="password")
    if st.button("Είσοδος"):
        if pwd == PASSWORD:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Λάθος κωδικός. Δοκιμάστε ξανά.")
    return False

# Αν ο κωδικός δεν είναι σωστός, σταματάει την εκτέλεση εδώ
if not check_password():
    st.stop()

# --- ΚΥΡΙΩΣ ΕΦΑΡΜΟΓΗ ---
# Αν φτάσει εδώ, σημαίνει ότι ο κωδικός είναι σωστός
st.title("🛠️ Σύστημα Διαχείρισης & AI Αναζήτησης Βλαβών")

db_url = os.environ.get("DB_URL")
engine = create_engine(db_url)

@st.cache_data(ttl=10)
def get_data():
    try:
        return pd.read_sql("SELECT * FROM faults", engine)
    except:
        return pd.DataFrame(columns=["ΤΟΜΕΑΣ", "ΠΕΡΙΓΡΑΦΗ", "ΗΜΕΡΟΜΗΝΙΑ", "ΑΝΤΑΛΛΑΚΤΙΚΑ"])

df = get_data()

# 1. Προσθήκη νέας βλάβης
with st.expander("➕ Προσθήκη νέας βλάβης στο ιστορικό"):
    with st.form("add_fault", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tomeas = st.text_input("Τομέας:")
            perigrafi = st.text_area("Περιγραφή:")
        with col2:
            imera = st.text_input("Ημερομηνία (π.χ. 08/03/2026):")
            antal = st.text_input("Ανταλλακτικά:")
        
        if st.form_submit_button("Αποθήκευση στη βάση"):
            if tomeas and perigrafi:
                with engine.connect() as conn:
                    conn.execute(text('INSERT INTO faults ("ΤΟΜΕΑΣ", "ΠΕΡΙΓΡΑΦΗ", "ΗΜΕΡΟΜΗΝΙΑ", "ΑΝΤΑΛΛΑΚΤΙΚΑ") VALUES (:t, :p, :h, :a)'), 
                                 {"t": tomeas, "p": perigrafi, "h": imera, "a": antal})
                    conn.commit()
                st.success("✅ Η βλάβη προστέθηκε επιτυχώς!")
                st.rerun()
            else:
                st.warning("⚠️ Παρακαλώ συμπληρώστε τουλάχιστον Τομέα και Περιγραφή.")

# 2. AI Αναζήτηση
st.divider()
st.subheader("🔍 Αναζήτηση στο Ιστορικό")
user_input = st.text_input("Περιγράψτε τη βλάβη που ψάχνετε:")

if user_input and not df.empty:
    results = []
    for _, row in df.iterrows():
        score = fuzz.token_sort_ratio(user_input.lower(), str(row['ΠΕΡΙΓΡΑΦΗ']).lower())
        if score > 30:
            results.append({
                "ΤΟΜΕΑΣ": row['ΤΟΜΕΑΣ'],
                "ΠΕΡΙΓΡΑΦΗ": row['ΠΕΡΙΓΡΑΦΗ'],
                "ΗΜΕΡΟΜΗΝΙΑ": row['ΗΜΕΡΟΜΗΝΙΑ'],
                "ΑΝΤΑΛΛΑΚΤΙΚΑ": row['ΑΝΤΑΛΛΑΚΤΙΚΑ'],
                "ΟΜΟΙΟΤΗΤΑ": f"{score}%"
            })
    
    if results:
        res_df = pd.DataFrame(results).sort_values(by="ΟΜΟΙΟΤΗΤΑ", ascending=False)
        st.table(res_df)
    else:
        st.info("ℹ️ Δεν βρέθηκαν παρόμοιες βλάβες.")

# 3. Backup
st.divider()
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Κατέβασμα αντιγράφου (Backup CSV)",
        data=csv,
        file_name='faults_backup.csv',
        mime='text/csv',
    )
