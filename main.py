import os
import streamlit as st
from sqlalchemy import create_engine

@st.cache_resource
def get_engine():
    # Προσπαθεί να διαβάσει από τα Environment Variables του Render
    # Αν δεν βρει, τότε ψάχνει στα secrets του Streamlit (αν το τρέχεις τοπικά)
    db_url = os.environ.get("DB_URL")
    if not db_url:
        db_url = st.secrets.get("DB_URL")
    
    if not db_url:
        st.error("Το DB_URL δεν βρέθηκε!")
        st.stop()
        
    return create_engine(db_url)






