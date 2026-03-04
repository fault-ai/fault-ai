import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Fault AI", layout="wide")
st.title("🔧 Αναζήτηση & Καταγραφή Βλαβών")

EXCEL_FILE = "Αναφορα Βλαβων.xlsx"

# -------------------- 1. Φόρτωση Excel --------------------
@st.cache_data
def load_excel():
    all_sheets = pd.read_excel(EXCEL_FILE, sheet_name=None)
    df = pd.concat(all_sheets.values(), ignore_index=True)
    return df

df = load_excel()
st.write(f"📊 Φορτώθηκαν {len(df)} εγγραφές από {len(pd.read_excel(EXCEL_FILE, sheet_name=None))} φύλλα.")

# -------------------- 2. Μοντέλο embeddings --------------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# -------------------- 3. Δημιουργία FAISS index --------------------
@st.cache_resource
def create_index(df):
    embeddings = model.encode(df["ΠΕΡΙΓΡΑΦΗ"].tolist(), convert_to_numpy=True)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    return index, embeddings

index, embeddings = create_index(df)

# -------------------- 4. Συνάρτηση αναζήτησης --------------------
def search_fault(query, top_k=5, threshold=0.4):
    q_emb = model.encode([query], convert_to_numpy=True)
    q_emb = q_emb / np.linalg.norm(q_emb, axis=1, keepdims=True)
    D, I = index.search(q_emb, top_k*2)
    results = []
    scores = []
    for score, idx in zip(D[0], I[0]):
        if score >= threshold and idx not in results:
            results.append(idx)
            scores.append(score)
        if len(results) >= top_k:
            break
    return df.iloc[results].copy(), scores

# -------------------- 5. Αναζήτηση βλάβης --------------------
st.subheader("🔎 Αναζήτηση Ιστορικών Βλαβών")
fault_now = st.text_input("Δώσε περιγραφή τρέχουσας βλάβης:")

if fault_now:
    results, scores = search_fault(fault_now)
    if results.empty:
        st.warning("⚠️ Δεν βρέθηκαν σχετικές βλάβες με αρκετή ομοιότητα.")
    else:
        results["Ομοιότητα"] = [f"{s*100:.1f}%" for s in scores]
        st.dataframe(results[['ΤΟΜΕΑΣ','ΗΜΕΡΟΜΗΝΙΑ','ΠΕΡΙΓΡΑΦΗ','ΑΝΤΑΛΛΑΚΤΙΚΑ','Ομοιότητα']])

# -------------------- 6. Προσθήκη νέας βλάβης --------------------
st.subheader("➕ Καταγραφή Νέας Βλάβης")
with st.form("new_fault_form"):
    col1, col2 = st.columns(2)
    with col1:
        tomes = st.text_input("ΤΟΜΕΑΣ")
        date = st.date_input("ΗΜΕΡΟΜΗΝΙΑ", datetime.today())
    with col2:
        desc = st.text_area("ΠΕΡΙΓΡΑΦΗ")
        parts = st.text_input("ΑΝΤΑΛΛΑΚΤΙΚΑ")
    
    submitted = st.form_submit_button("Προσθήκη Βλάβης")
    
    if submitted:
        if not desc.strip():
            st.error("Η περιγραφή δεν μπορεί να είναι κενή!")
        else:
            new_row = {
                "ΤΟΜΕΑΣ": tomes,
                "ΗΜΕΡΟΜΗΝΙΑ": date,
                "ΠΕΡΙΓΡΑΦΗ": desc,
                "ΑΝΤΑΛΛΑΚΤΙΚΑ": parts
            }
            df.loc[len(df)] = new_row
            df.to_excel(EXCEL_FILE, index=False)
            st.success("✅ Νέα βλάβη καταχωρήθηκε στο Excel!")

            # Ανανεώνουμε embeddings και FAISS index
            index, embeddings = create_index(df)
            st.info("📦 Embeddings και index ανανεώθηκαν!")






