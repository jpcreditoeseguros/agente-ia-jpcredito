import streamlit as st
import pandas as pd
import openai
import os

# Vai buscar a API Key aos Secrets da Streamlit Cloud
openai.api_key = os.environ.get("OPENAI_API_KEY")

st.title('Análise Inteligente de Mapas Comparativos JP Crédito e Seguros')

uploaded_file = st.file_uploader("Faz upload do ficheiro Excel (.xlsx)")

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0)
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
