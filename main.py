import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text
from fuzzywuzzy import fuzz

# --- ΡΥΘΜΙΣΗ ΑΣΦΑΛΕΙΑΣ ---
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
            st.error("❌ Λάθος κωδικός.")
    return False

if not check_password():
    st.stop()

# --- ΣΥΝΔΕΣΗ & ΑΥΤΟΜΑΤΗ ΑΝΑΒΑΘΜΙΣΗ ΒΑΣΗΣ ---
st.title("🛠️ Σύστημα Διαχείρισης & AI Αναζήτησης Βλαβών")
db_url = os.environ.get("DB_URL")
engine = create_engine(db_url)

# Αυτόματα προσθέτει τη στήλη serial_number αν δεν υπάρχει
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE faults ADD COLUMN IF NOT EXISTS "serial_number" TEXT;'))
    conn.commit()

@st.cache_data(ttl=10)
def get_data():
    try:
        return pd.read_sql("SELECT * FROM faults", engine)
    except:
        return pd.DataFrame(columns=["ΤΟΜΕΑΣ", "ΠΕΡΙΓΡΑΦΗ", "ΗΜΕΡΟΜΗΝΙΑ", "ΑΝΤΑΛΛΑΚΤΙΚΑ", "serial_number"])

df = get_data()

# 1. Προσθήκη νέας βλάβης
with st.expander("➕ Προσθήκη νέας βλάβης"):
    with st.form("add_fault", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tomeas = st.text_input("Τομέας:")
            perigrafi = st.text_area("Περιγραφή:")
        with col2:
            imera = st.text_input("Ημερομηνία (π.χ. 08/03/2026):")
            antal = st.text_input("Ανταλλακτικά:")
            serial = st.text_input("Serial Number:")
        
        if st.form_submit_button("Αποθήκευση"):
            if tomeas and perigrafi:
                with engine.connect() as conn:
                    conn.execute(text('INSERT INTO faults ("ΤΟΜΕΑΣ", "ΠΕΡΙΓΡΑΦΗ", "ΗΜΕΡΟΜΗΝΙΑ", "ΑΝΤΑΛΛΑΚΤΙΚΑ", "serial_number") VALUES (:t, :p, :h, :a, :s)'), 
                                   {"t": tomeas, "p": perigrafi, "h": imera, "a": antal, "s": serial})
                    conn.commit()
                st.success("✅ Καταχωρήθηκε!")
                st.rerun()
            else:
                st.warning("⚠️ Συμπληρώστε Τομέα και Περιγραφή.")

# 2. AI Αναζήτηση & Serial Number Search
st.divider()
st.subheader("🔍 Αναζήτηση")
search_type = st.radio("Τύπος:", ["AI (Ομοιότητες)", "Αναζήτηση με Serial Number"])

if search_type == "Αναζήτηση με Serial Number":
    sn_input = st.text_input("Εισάγετε Serial Number:")
    if sn_input:
        res = df[df['serial_number'].str.contains(sn_input, case=False, na=False)]
        st.table(res)
else:
    user_input = st.text_input("Περιγράψτε τη βλάβη (π.χ. 'χαμηλή τάση'):")
    if user_input and not df.empty:
        results = []
        for _, row in df.iterrows():
            desc = str(row['ΠΕΡΙΓΡΑΦΗ']).lower()
            query = user_input.lower()
            
            # --- ΒΕΛΤΙΩΣΗ: Πιο αυστηρό σκοράρισμα ---
            # Χρησιμοποιούμε token_set_ratio για να πιάσουμε καλύτερα τις λέξεις
            score = fuzz.token_set_ratio(query, desc)
            
            # Ανεβάζουμε το όριο στο 65 για να είναι πιο σχετικά τα αποτελέσματα
            if score > 65:
                row_dict = row.to_dict()
                row_dict['ΟΜΟΙΟΤΗΤΑ'] = f"{score}%"
                results.append(row_dict)
        
        if results:
            res_df = pd.DataFrame(results).sort_values(by="ΟΜΟΙΟΤΗΤΑ", ascending=False)
            st.table(res_df)
        else:
            st.info("ℹ️ Δεν βρέθηκαν πολύ σχετικά αποτελέσματα. Δοκιμάστε πιο συγκεκριμένες λέξεις.")
# 3. Backup
st.divider()
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Κατέβασμα Backup (CSV)", csv, 'faults_backup.csv', 'text/csv')
