import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Ρύθμιση σελίδας
st.set_page_config(page_title="Fault AI", layout="wide")

# Σύνδεση με τη βάση
@st.cache_resource
def get_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(db_url)

engine = get_engine()

st.title("🛠️ Σύστημα Διαχείρισης Βλαβών")

# Αναζήτηση
st.subheader("🔍 Αναζήτηση")
search_query = st.text_input("Περιγραφή βλάβης ή Μηχάνημα:")

if search_query:
    query = f"SELECT * FROM faults WHERE fault_description ILIKE '%%{search_query}%%' OR machine ILIKE '%%{search_query}%%'"
    df = pd.read_sql(query, engine)
    st.dataframe(df, use_container_width=True)

st.divider()

# Καταχώρηση
st.subheader("📝 Νέα Καταχώρηση")
with st.form("new_fault_form"):
    machine = st.text_input("Όνομα Μηχανήματος")
    fault_desc = st.text_area("Περιγραφή Βλάβης")
    solution = st.text_area("Προτεινόμενη Λύση")
    
    if st.form_submit_button("Αποθήκευση"):
        new_row = pd.DataFrame([{'machine': machine, 'fault_description': fault_desc, 'solution': solution}])
        new_row.to_sql('faults', engine, if_exists='append', index=False)
        st.success("Η βλάβη αποθηκεύτηκε!")






