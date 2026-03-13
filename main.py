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

# --- ΣΥΝΔΕΣΗ ΒΑΣΗΣ ---
st.title("🛠️ Σύστημα Διαχείρισης & AI Αναζήτησης Βλαβών")

# Παίρνουμε το URL από τις ρυθμίσεις του Render
db_url = os.environ.get("DB_URL")
if not db_url:
    st.error("⚠️ Το DB_URL δεν βρέθηκε στις ρυθμίσεις του Render!")
    st.stop()

engine = create_engine(db_url)

# Συνάρτηση για ανάκτηση δεδομένων
def get_data():
    try:
        # Χωρίς cache για να παίρνει πάντα τα πιο πρόσφατα δεδομένα
        return pd.read_sql("SELECT * FROM faults", engine)
    except Exception as e:
        st.error(f"❌ Σφάλμα ανάγνωσης βάσης: {e}")
        return pd.DataFrame()

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
                try:
                    with engine.connect() as conn:
                        conn.execute(text('INSERT INTO faults ("ΤΟΜΕΑΣ", "ΠΕΡΙΓΡΑΦΗ", "ΗΜΕΡΟΜΗΝΙΑ", "ΑΝΤΑΛΛΑΚΤΙΚΑ", "serial_number") VALUES (:t, :p, :h, :a, :s)'), 
                                     {"t": tomeas, "p": perigrafi, "h": imera, "a": antal, "s": serial})
                        conn.commit()
                    st.success("✅ Καταχωρήθηκε!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Σφάλμα αποθήκευσης: {e}")
            else:
                st.warning("⚠️ Συμπληρώστε Τομέα και Περιγραφή.")

# 2. Αναζήτηση
st.divider()
st.subheader("🔍 Αναζήτηση")
if not df.empty:
    search_type = st.radio("Τύπος:", ["AI (Ομοιότητες)", "Αναζήτηση με Serial Number"])

    if search_type == "Αναζήτηση με Serial Number":
        sn_input = st.text_input("Εισάγετε Serial Number:")
        if sn_input:
            res = df[df['serial_number'].str.contains(sn_input, case=False, na=False)]
            st.table(res)
    else:
        user_input = st.text_input("Περιγράψτε τη βλάβη:")
        if user_input:
            results = []
            for _, row in df.iterrows():
                desc = str(row['ΠΕΡΙΓΡΑΦΗ']).lower()
                score = fuzz.token_set_ratio(user_input.lower(), desc)
                if score > 65:
                    row_dict = row.to_dict()
                    row_dict['ΟΜΟΙΟΤΗΤΑ'] = f"{score}%"
                    results.append(row_dict)
            
            if results:
                st.table(pd.DataFrame(results).sort_values(by="ΟΜΟΙΟΤΗΤΑ", ascending=False))
            else:
                st.info("ℹ️ Δεν βρέθηκαν σχετικά αποτελέσματα.")
else:
    st.info("ℹ️ Η βάση είναι άδεια ή δεν υπάρχουν δεδομένα.")

# 3. Backup
st.divider()
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Κατέβασμα Backup (CSV)", csv, 'faults_backup.csv', 'text/csv')
