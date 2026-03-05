import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text

st.title("🛠️ Σύστημα Διαχείρισης Βλαβών")

db_url = os.environ.get("DB_URL")
engine = create_engine(db_url)

# 1. Δημιουργία πίνακα αν δεν υπάρχει
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE IF NOT EXISTS faults (id SERIAL PRIMARY KEY, fault_description TEXT, solution TEXT)"))
    conn.commit()

# 2. Φόρμα για νέα καταχώρηση
with st.form("new_fault"):
    desc = st.text_input("Περιγραφή βλάβης:")
    sol = st.text_input("Λύση:")
    submitted = st.form_submit_button("Αποθήκευση")
    if submitted:
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO faults (fault_description, solution) VALUES (:d, :s)"), {"d": desc, "s": sol})
            conn.commit()
        st.success("Η βλάβη αποθηκεύτηκε!")

# 3. Εμφάνιση όλων των δεδομένων
st.subheader("Βάση Δεδομένων:")
df = pd.read_sql("SELECT * FROM faults", engine)
st.dataframe(df)





