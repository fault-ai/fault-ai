import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# 1. Φόρτωση μοντέλου AI (με cache για ταχύτητα)
@st.cache_resource
def load_ai_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

# 2. Σύνδεση στη Βάση
@st.cache_resource
def get_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(db_url)

model = load_ai_model()
engine = get_engine()

st.title("🤖 AI Fault Finder")

# 3. Αναζήτηση
search_text = st.text_input("Περίγραψε τη βλάβη:")

if search_text:
    # Εδώ θα έμπαινε η λογική για FAISS + SQL
    st.write("Αναζήτηση νοήματος για:", search_text)
    # Προσθήκη αποτελεσμάτων από την SQL βάση σου
    query = "SELECT * FROM faults LIMIT 5"
    df = pd.read_sql(query, engine)
    st.dataframe(df)






