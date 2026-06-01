import streamlit as st
import pandas as pd
from Bio.SeqUtils.ProtParam import ProteinAnalysis

st.title("AI-Antibody Developability Filter")
st.write("連携: Protein Hydrophobicity Profiler")

uploaded_file = st.file_uploader("Upload CSV (columns: id, sequence)", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    results = []
    for _, row in df.iterrows():
        try:
            pa = ProteinAnalysis(row['sequence'].upper())
            results.append({"id": row['id'], "pI": pa.isoelectric_point(), "GRAVY": pa.gravy()})
        except:
            pass
    
    res_df = pd.DataFrame(results)
    st.dataframe(res_df)
    
    passed = res_df[(res_df['GRAVY'] < 0) & (res_df['pI'] < 9.0)]
    st.success(f"{len(df)} 件中 {len(passed)} 件が開発可能性フィルタを通過しました。")
    st.dataframe(passed)
