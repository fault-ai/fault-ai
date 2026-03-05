import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Σύνδεση με τη βάση
@st.cache_resource
def get_engine():
    # Βεβαιώσου ότι έχεις ορίσει το DB_URL στα Environment Variables του Render
    db_url = st.secrets["DB_URL"] 
    return create_engine(db_url)

engine = get_engine()

st.title("🛠️ Σύστημα Διαχείρισης Βλαβών")

# Αναζήτηση
search = st.text_input("Αναζήτηση βλάβης:")
if search:
    query = f"SELECT * FROM faults WHERE fault_description ILIKE '%%{search}%%'"
    df = pd.read_sql(query, engine)
    st.dataframe(df)






