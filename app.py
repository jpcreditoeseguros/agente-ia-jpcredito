import streamlit as st
import pandas as pd
import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

st.title('Análise Inteligente de Mapas Comparativos JP Crédito e Seguros')

uploaded_file = st.file_uploader("Faz upload do ficheiro Excel (.xlsx)")

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet = st.selectbox(
        "Escolhe a folha a analisar:",
        xls.sheet_names,
        index=xls.sheet_names.index("MAPA COMPARATIVO") if "MAPA COMPARATIVO" in xls.sheet_names else 0
    )
    df = pd.read_excel(uploaded_file, sheet_name=sheet)
    st.write("Primeiras linhas do ficheiro:")
    st.write(df.head())

    colunas = [col.lower() for col in df.columns]
    tem_situacao_atual = any("situação atual" in col for col in colunas)

    if sheet.lower() == "dados":
        prompt = f"""
        Atua como um especialista em crédito habitação.
        O teu objetivo é preparar uma defesa técnica do processo, para envio ao banco e facilitar a aprovação do crédito.
        Analisa detalhadamente todos os dados apresentados na tabela (aba 'Dados') e identifica:
        - Pontos fortes do processo e dos proponentes;
        - Argumentos que favorecem a aprovação (rendimento, taxa de esforço, estabilidade laboral, garantias, etc.);
        - Como apresentar o caso para minimizar dúvidas do banco;
        - Sugere frases de justificação e pontos de destaque para colocar na comunicação ao banco.
        Utiliza sempre linguagem profissional e segura, como um verdadeiro intermediário de crédito.
        Tabela de dados:
        {df.head(20).to_string(index=False)}
        """
    else:
        dor_principal = st.selectbox(
            "Qual a principal dor do cliente?",
            [
                "Preço/prestação",
                "Juntar vários créditos",
                "Retirar seguros do banco",
                "Retirar o ex do crédito",
                "Pedir liquidez adicional",
                "Mudar tipo de taxa"
            ]
        )

        if tem_situacao_atual:
            comparacao = """
            Existe uma coluna “Situação Atual”, por isso deves comparar cada aspeto entre a proposta atual e as novas, e realçar as melhorias e a poupança gerada para o cliente.
            """
        else:
            comparacao = """
            Não existe coluna “Situação Atual”, por isso não faças referência a transferências. Foca-te em analisar as propostas como novas operações.
            """

        prompt = f"""
        Atua como um especialista em crédito habitação.
        O teu objetivo é analisar tecnicamente a folha 'Mapa comparativo' e ajudar o gestor a defender as várias propostas junto do cliente, de forma clara, detalhada e objetiva.
        Considera que a principal dor do cliente é: **{dor_principal}**.

        Para cada proposta apresentada na tabela, compara e realça de forma explícita e organizada os seguintes aspetos essenciais (se existirem na tabela):
        - Nome do banco
        - Montante de financiamento proposto
        - Prazo do empréstimo
        - Prestação mensal **com seguros**
        - Valor total dos seguros (diz sempre se são contratados dentro do banco ou fora)
        - TAN bonificada (Taxa Anual Nominal)
        - Tipo de taxa (fixa, variável, mista, etc.)
        - Valor total dos custos associados com o crédito (inclui todas as comissões, impostos, despesas processuais e outros encargos únicos)

        Para cada um destes pontos, destaca as diferenças entre as propostas, apresentando de forma sintética os prós e contras de cada solução.

        {comparacao}

        No final, identifica qual a proposta mais vantajosa tendo em conta a dor do cliente, e prepara argumentos claros para defender essa solução junto do cliente, antecipando e rebatendo objeções comuns.

        Termina sempre com uma frase de fecho forte, a incentivar o cliente a avançar para a formalização.

        Tabela de dados:
        {df.head(20).to_string(index=False)}
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
