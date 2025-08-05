import streamlit as st
import pandas as pd
import openai

# Coloca aqui a tua OpenAI API Key
openai.api_key = "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"

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
        resposta = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Responder como um gestor de crédito experiente."},
                      {"role": "user", "content": prompt}],
            max_tokens=1200,
            temperature=0.2
        )
        st.write("Resposta da IA:")
        st.write(resposta.choices[0].message.content)
