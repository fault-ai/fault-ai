import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine

st.set_page_config(page_title="Fault AI", layout="wide")
st.title("🛠️ Σύστημα Διαχείρισης Βλαβών")

# 1. Έλεγχος αν υπάρχει το URL
db_url = os.environ.get("DB_URL")

if not db_url:
    st.error("Σφάλμα: Δεν βρέθηκε το DB_URL στις ρυθμίσεις του Render!")
    st.stop()

# 2. Σύνδεση με τη βάση
try:
    engine = create_engine(db_url)
    # Δοκιμή σύνδεσης
    with engine.connect() as conn:
        st.success("✅ Επιτυχής σύνδεση στη βάση δεδομένων!")
except Exception as e:
    st.error(f"❌ Σφάλμα σύνδεσης στη βάση: {e}")
    st.stop()

# 3. Απλή εμφάνιση για επιβεβαίωση
st.write("Η εφαρμογή τρέχει κανονικά!")

# Αναζήτηση
search_query = st.text_input("Περιγραφή βλάβης:")
if search_query:
    st.write(f"Ψάχνεις για: {search_query}")






