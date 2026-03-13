import streamlit as st
import pandas as pd
import psycopg2
import os
from sqlalchemy import create_engine

# 1. Ρύθμιση Σύνδεσης
DB_URL = os.environ.get("DB_URL") # Χρησιμοποιούμε το όνομα που δουλεύει στο Render σου
engine = create_engine(DB_URL)

st.title("🔧 Σύστημα Διαχείρισης & AI Αναζήτησης Βλαβών")

# 2. Φόρμα Καταχώρησης
with st.form("fault_entry_form"):
    st.subheader("Καταχώρηση Νέας Βλάβης")
    col1, col2 = st.columns(2)
    with col1:
        vehicle = st.text_input("Όχημα")
        mechanism = st.text_input("Μηχανισμός")
    with col2:
        serial_number = st.text_input("Serial Number")
        date = st.date_input("Ημερομηνία")
    
    notes = st.text_area("Περιγραφή Βλάβης/Συντήρησης")
    
    submit_button = st.form_submit_button("Αποθήκευση στη Μνήμη")
    
    if submit_button:
        # SQL Insert με το νέο πεδίο serial_number
        query = "INSERT INTO faults (\"ΟΧΗΜΑ\", \"ΜΗΧΑΝΙΣΜΟΣ\", \"ΗΜΕΡΟΜΗΝΙΑ\", \"ΠΑΡΑΤΗΡΗΣΕΙΣ\", \"serial_number\") VALUES (%s, %s, %s, %s, %s)"
        with engine.connect() as conn:
            conn.execute(query, (vehicle, mechanism, date, notes, serial_number))
            conn.commit()
        st.success(f"Επιτυχία! Το Serial Number {serial_number} καταχωρήθηκε.")

st.divider()

# 3. Σύστημα Αναζήτησης με "Μνήμη"
st.subheader("Αναζήτηση Ιστορικού Εξαρτήματος")
search_sn = st.text_input("Εισάγετε Serial Number για εμφάνιση ιστορικού:")

if search_sn:
    query = f"SELECT * FROM faults WHERE serial_number = '{search_sn}' ORDER BY \"ΗΜΕΡΟΜΗΝΙΑ\" DESC"
    try:
        df_history = pd.read_sql(query, engine)
        
        if not df_history.empty:
            st.write(f"Βρέθηκαν {len(df_history)} εγγραφές για το {search_sn}:")
            st.dataframe(df_history)
        else:
            st.warning("Δεν βρέθηκε ιστορικό για αυτό το Serial Number.")
    except Exception as e:
        st.error(f"Σφάλμα κατά την αναζήτηση: {e}")
st.divider()
st.subheader("🤖 AI Ανάλυση & Αναζήτηση Ομοιοτήτων")

# Εδώ εισάγουμε το query για το AI
user_query = st.text_input("Περιγράψτε τι ψάχνετε (π.χ. 'παρόμοιες βλάβες στον κινητήρα'):")

if user_query:
    # 1. Τραβάμε τα δεδομένα από τη βάση
    query_all = 'SELECT "ΜΗΧΑΝΙΣΜΟΣ", "ΠΑΡΑΤΗΡΗΣΕΙΣ" FROM faults'
    df_ai = pd.read_sql(query_all, engine)
    
    # 2. Απλή λογική αναζήτησης (ή κλήση σε AI API)
    # Θα δείξουμε όσα έχουν κοινές λέξεις με το query του χρήστη
    matches = df_ai[df_ai['ΠΑΡΑΤΗΡΗΣΕΙΣ'].str.contains(user_query, case=False, na=False)]
    
    if not matches.empty:
        st.write("Βρέθηκαν παρόμοιες περιπτώσεις:")
        st.dataframe(matches)
    else:
        st.info("Δεν βρέθηκαν παρόμοιες βλάβες με αυτά τα χαρακτηριστικά.")
