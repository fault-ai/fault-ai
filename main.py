import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text

st.title("🛠️ Σύστημα Διαχείρισης Βλαβών")

db_url = os.environ.get("DB_URL")
engine = create_engine(db_url)

# 1. Φόρμα καταχώρησης με τα σωστά ονόματα στηλών (ΤΟΜΕΑΣ, ΠΕΡΙΓΡΑΦΗ)
with st.form("new_fault", clear_on_submit=True):
    tomeas = st.text_input("Τομέας (π.χ. ΠΙΝΑΚΑΣ ΑΣΦΑΛΕΙΩΝ):")
    perigrafi = st.text_area("Περιγραφή Βλάβης:")
    submitted = st.form_submit_button("Αποθήκευση")
    
    if submitted:
        try:
            with engine.connect() as conn:
                # Χρησιμοποιούμε τα ονόματα που ήδη έχει ο πίνακας στη βάση σου
                conn.execute(
                    text('INSERT INTO faults ("ΤΟΜΕΑΣ", "ΠΕΡΙΓΡΑΦΗ") VALUES (:t, :p)'), 
                    {"t": tomeas, "p": perigrafi}
                )
                conn.commit()
            st.success("✅ Η βλάβη αποθηκεύτηκε επιτυχώς!")
        except Exception as e:
            st.error(f"❌ Σφάλμα αποθήκευσης: {e}")

# 2. Εμφάνιση πίνακα
st.subheader("Καταχωρημένες Βλάβες")
try:
    # Διαβάζουμε όλο τον πίνακα για να δούμε τα πάντα
    df = pd.read_sql("SELECT * FROM faults", engine)
    st.table(df) # Χρησιμοποιούμε st.table για πιο καθαρή εμφάνιση
except Exception as e:
    st.write("Δεν ήταν δυνατή η ανάγνωση των δεδομένων.")




