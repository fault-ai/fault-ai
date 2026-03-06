import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine
from fuzzywuzzy import fuzz

st.set_page_config(page_title="Fault AI - Similarity Search", layout="wide")
st.title("🤖 AI Αναζήτηση Ομοιότητας Βλαβών")

db_url = os.environ.get("DB_URL")
engine = create_engine(db_url)

# 1. Φόρτωση όλου του ιστορικού από τη βάση
@st.cache_data(ttl=60)
def load_all_data():
    try:
        return pd.read_sql("SELECT * FROM faults", engine)
    except Exception as e:
        st.error(f"Σφάλμα κατά τη φόρτωση: {e}")
        return pd.DataFrame()

df = load_all_data()

# 2. Εισαγωγή νέας βλάβης για έλεγχο
st.subheader("Αναζήτηση στο Ιστορικό")
user_query = st.text_input("Γράψτε τη βλάβη που αντιμετωπίζετε:")

if user_query and not df.empty:
    results = []
    
    for _, row in df.iterrows():
        # Υπολογισμός ομοιότητας (0-100)
        # Συγκρίνουμε το κείμενο του χρήστη με τη στήλη ΠΕΡΙΓΡΑΦΗ
        score = fuzz.token_set_ratio(user_query, str(row['ΠΕΡΙΓΡΑΦΗ']))
        
        results.append({
            "ΤΟΜΕΑΣ": row.get('ΤΟΜΕΑΣ', 'N/A'),
            "ΠΕΡΙΓΡΑΦΗ ΙΣΤΟΡΙΚΟΥ": row.get('ΠΕΡΙΓΡΑΦΗ', 'N/A'),
            "ΑΝΤΑΛΛΑΚΤΙΚΑ": row.get('ΑΝΤΑΛΛΑΚΤΙΚΑ', '-'),
            "ΟΜΟΙΟΤΗΤΑ": f"{score}%",
            "raw_score": score
        })
    
    # Μετατροπή σε DataFrame και ταξινόμηση από το μεγαλύτερο ποσοστό στο μικρότερο
    res_df = pd.DataFrame(results).sort_values(by="raw_score", ascending=False)
    
    # Εμφάνιση των πιο σχετικών (π.χ. πάνω από 40% ομοιότητα)
    st.write(f"Βρέθηκαν {len(res_df[res_df['raw_score'] > 40])} σχετικές εγγραφές:")
    st.table(res_df[res_df['raw_score'] > 20].drop(columns=['raw_score']).head(10))

elif df.empty:
    st.warning("Η βάση δεδομένων φαίνεται να είναι άδεια ή δεν διαβάστηκε σωστά.")

