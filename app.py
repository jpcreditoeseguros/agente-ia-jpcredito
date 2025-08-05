import streamlit as st
import pandas as pd
import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

st.title('Análise Inteligente de Mapas Comparativos JP Crédito e Seguros')

uploaded_file = st.file_uploader("Faz upload do ficheiro Excel (.xlsx)")

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet = st.selectbox("Escolhe a folha a analisar:", xls.sheet_names, index=xls.sheet_names.index("MAPA COMPARATIVO") if "MAPA COMPARATIVO" in xls.sheet_names else 0)
    df = pd.read_excel(uploaded_file, sheet_name=sheet)
    st.write("Primeiras linhas do ficheiro:")
    st.write(df.head())

    prompt = f"""
    És um especialista em crédito habitação. Analisa esta tabela de propostas e responde ao gestor:
    {df.head(20).to_string(index=False)}
    Resumo, tabela comparativa, argumentos e frase de fecho.
    """

    if st.button("Obter análise IA"):
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Responder como um gestor de crédito experiente."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.2
        )
        st.write("Resposta da IA:")
        st.write(response.choices[0].message.content)
