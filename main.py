import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# 1. Ρύθμιση για να μην "κρασάρει" το tablet
st.set_page_config(page_title="Fault AI", layout="wide")

st.title("🛠️ Σύστημα Διαχείρισης Βλαβών")

# 2. Σύνδεση με τη βάση από τα Secrets
@st.cache_resource
def get_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(db_url)

engine = get_engine()

# 3. Αναζήτηση Βλαβών
st.subheader("🔍 Αναζήτηση")
search = st.text_input("Γράψε λέξη-κλειδί:")

if search:
    query = f"SELECT * FROM faults WHERE fault_description ILIKE '%%{search}%%'"
    try:
        df = pd.read_sql(query, engine)
        st.dataframe(df)
    except:
        st.write("Δεν βρέθηκαν αποτελέσματα.")

# 4. Καταχώρηση (χωρίς Excel)
st.subheader("📝 Νέα Βλάβη")
with st.form("add_fault"):
    machine = st.text_input("Μηχάνημα")
    fault = st.text_area("Περιγραφή")
    sol = st.text_area("Λύση")
    if st.form_submit_button("Αποθήκευση"):
        new_data = pd.DataFrame([{'machine': machine, 'fault_description': fault, 'solution': sol}])
        new_data.to_sql('faults', engine, if_exists='append', index=False)
        st.success("Επιτυχία!")






