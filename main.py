import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text

st.title("🛠️ Σύστημα Διαχείρισης Βλαβών")

db_url = os.environ.get("DB_URL")
engine = create_engine(db_url)

# 1. Δημιουργία πίνακα με πιο σίγουρο τρόπο
try:
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS faults (
                id SERIAL PRIMARY KEY, 
                fault_description TEXT, 
                solution TEXT
            )
        """))
        conn.commit()
except Exception as e:
    st.error(f"Σφάλμα δημιουργίας πίνακα: {e}")

# 2. Φόρμα καταχώρησης
with st.form("new_fault", clear_on_submit=True):
    desc = st.text_input("Περιγραφή βλάβης:")
    sol = st.text_input("Λύση:")
    submitted = st.form_submit_button("Αποθήκευση")
    
    if submitted:
        try:
            with engine.connect() as conn:
                conn.execute(
                    text("INSERT INTO faults (fault_description, solution) VALUES (:d, :s)"), 
                    {"d": desc, "s": sol}
                )
                conn.commit()
            st.success("✅ Η βλάβη αποθηκεύτηκε!")
        except Exception as e:
            st.error(f"❌ Σφάλμα αποθήκευσης: {e}")

# 3. Εμφάνιση πίνακα
st.subheader("Καταχωρημένες Βλάβες")
try:
    df = pd.read_sql("SELECT * FROM faults", engine)
    st.dataframe(df)
except:
    st.write("Δεν υπάρχουν ακόμα δεδομένα.")




