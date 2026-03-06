import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text
from fuzzywuzzy import fuzz

st.set_page_config(page_title="Fault AI Pro", layout="wide")
st.title("🛠️ Σύστημα Διαχείρισης & AI Αναζήτησης Βλαβών")

db_url = os.environ.get("DB_URL")
engine = create_engine(db_url)

# Φόρτωση δεδομένων
@st.cache_data(ttl=10) # Μικρό TTL για να βλέπεις άμεσα τις νέες εγγραφές
def get_data():
    return pd.read_sql("SELECT * FROM faults", engine)

df = get_data()

# --- Τμήμα 1: Καταχώρηση Νέας Βλάβης ---
with st.expander("➕ Προσθήκη νέας βλάβης στο ιστορικό"):
    with st.form("add_fault", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tomeas = st.text_input("Τομέας:")
            perigrafi = st.text_area("Περιγραφή:")
        with col2:
            imera = st.text_input("Ημερομηνία (π.χ. 6/3/2026):")
            antal = st.text_input("Ανταλλακτικά:")
        
        submitted = st.form_submit_button("Αποθήκευση στη βάση")
        
        if submitted:
            with engine.connect() as conn:
                conn.execute(text('INSERT INTO faults ("ΤΟΜΕΑΣ", "ΠΕΡΙΓΡΑΦΗ", "ΗΜΕΡΟΜΗΝΙΑ", "ΑΝΤΑΛΛΑΚΤΙΚΑ") VALUES (:t, :p, :h, :a)'), 
                             {"t": tomeas, "p": perigrafi, "h": imera, "a": antal})
                conn.commit()
            st.success("Η βλάβη προστέθηκε επιτυχώς!")
            st.rerun()

# --- Τμήμα 2: AI Αναζήτηση ---
st.divider()
st.subheader("🔍 Αναζήτηση στο Ιστορικό")
user_input = st.text_input("Περιγράψτε τη βλάβη που αντιμετωπίζετε:")

if user_input and not df.empty:
    results = []
    for _, row in df.iterrows():
        score = fuzz.token_sort_ratio(user_input, str(row['ΠΕΡΙΓΡΑΦΗ']))
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
        st.info("Δεν βρέθηκαν παρόμοιες βλάβες.")
