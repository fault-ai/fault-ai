import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Ρύθμιση σελίδας
st.set_page_config(page_title="Fault AI", layout="wide")

# Σύνδεση με τη βάση μέσω των Secrets
@st.cache_resource
def get_engine():
    # Αυτό τραβάει το URL από τα Secrets που έβαλες στο Streamlit Cloud
    db_url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(db_url)

engine = get_engine()

st.title("🛠️ Σύστημα Διαχείρισης Βλαβών")

# --- Τμήμα Αναζήτησης ---
st.subheader("🔍 Αναζήτηση")
search_query = st.text_input("Περιγραφή βλάβης ή Μηχάνημα:")

if search_query:
    # Χρησιμοποιούμε ILIKE για αναζήτηση χωρίς θέμα πεζών/κεφαλαίων
    query = f"SELECT * FROM faults WHERE fault_description ILIKE '%%{search_query}%%' OR machine ILIKE '%%{search_query}%%'"
    try:
        df = pd.read_sql(query, engine)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Δεν βρέθηκαν αποτελέσματα.")
    except Exception as e:
        st.error(f"Σφάλμα σύνδεσης με τη βάση: {e}")

st.divider()

# --- Τμήμα Καταχώρησης ---
st.subheader("📝 Νέα Καταχώρηση")
with st.form("new_fault_form"):
    machine = st.text_input("Όνομα Μηχανήματος")
    fault_desc = st.text_area("Περιγραφή Βλάβης")
    solution = st.text_area("Προτεινόμενη Λύση")
    
    if st.form_submit_button("Αποθήκευση"):
        if machine and fault_desc:
            try:
                new_row = pd.DataFrame([{'machine': machine, 'fault_description': fault_desc, 'solution': solution}])
                new_row.to_sql('faults', engine, if_exists='append', index=False)
                st.success("Η βλάβη αποθηκεύτηκε!")
            except Exception as e:
                st.error(f"Σφάλμα κατά την αποθήκευση: {e}")
        else:
            st.warning("Παρακαλώ συμπληρώστε τα πεδία.")






