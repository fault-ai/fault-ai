import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine
from fuzzywuzzy import fuzz

st.title("🤖 AI Αναζήτηση Βλαβών (Similarity)")

db_url = os.environ.get("DB_URL")
engine = create_engine(db_url)

# 1. Φόρτωση Ιστορικού
@st.cache_data(ttl=60) # Ανανέωση κάθε λεπτό
def load_history():
    return pd.read_sql("SELECT * FROM faults", engine)

df = load_history()

# 2. Πεδίο Αναζήτησης
user_input = st.text_input("Περιγράψτε τη νέα βλάβη:")

if user_input:
    # Υπολογισμός ομοιότητας για κάθε εγγραφή στο ιστορικό
    results = []
    for index, row in df.iterrows():
        # Σύγκριση της εισαγωγής του χρήστη με τη στήλη "ΠΕΡΙΓΡΑΦΗ"
        similarity = fuzz.token_sort_ratio(user_input, str(row['ΠΕΡΙΓΡΑΦΗ']))
        
        results.append({
            "ΤΟΜΕΑΣ": row['ΤΟΜΕΑΣ'],
            "ΠΕΡΙΓΡΑΦΗ": row['ΠΕΡΙΓΡΑΦΗ'],
            "ΟΜΟΙΟΤΗΤΑ": f"{similarity}%",
            "score": similarity # για το sorting
        })
    
    # Μετατροπή σε DataFrame και ταξινόμηση (τα πιο όμοια πάνω)
    res_df = pd.DataFrame(results).sort_values(by="score", ascending=False)
    
    st.subheader("Πιθανές λύσεις από το ιστορικό:")
    # Δείξε μόνο όσα έχουν ομοιότητα πάνω από 30%
    st.table(res_df[res_df['score'] > 30].drop(columns=['score']))



