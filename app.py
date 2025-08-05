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

    # Campos que queres que a IA foque
    campos_relevantes = [
        "Montante Financiado",
        "Prazo",
        "PRESTAÇÃO COM SEGUROS",
        "Seguro de Vida Fora do Banco",
        "Seguro Multirriscos Banco",
        "TAN Bonificada",
        "Tipo de taxa",
        "Total de custos associados",
        "Situação Atual"
    ]

    # Filtrar só os campos relevantes (primeira coluna)
    if sheet.lower() == "mapa comparativo":
        df_filtrado = df[df[df.columns[0]].isin(campos_relevantes)]
    else:
        df_filtrado = df

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
        Só uses os campos exatamente como aparecem na tabela seguinte.
        Para cada banco, responde campo a campo, nunca inventes valores ou traduções, nem alteres o nome dos campos.
        Para cada proposta apresentada, responde sempre indicando:
        - Nome do banco (exatamente como está na tabela)
        - Montante Financiado
        - Prazo
        - PRESTAÇÃO COM SEGUROS
        - Seguro de Vida Fora do Banco
        - Seguro Multirriscos Banco
        - TAN Bonificada
        - Tipo de taxa
        - Total de custos associados
        - Situação Atual (se existir, para transferências)
        Se algum destes campos não existir na tabela, escreve “não consta na tabela”.

        {comparacao}

        No final, identifica qual a proposta mais vantajosa para a dor do cliente, prepara argumentos claros para defender essa solução junto do cliente, antecipando e rebatendo objeções comuns.

        Termina sempre com uma frase de fecho forte, a incentivar o cliente a avançar para a formalização.

        Tabela de dados (apenas campos essenciais, transposta para facilitar leitura):
        {df_filtrado.T.to_string()}
        """

    if st.button("Obter análise IA"):
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Responder como um gestor de crédito experiente."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1400,
            temperature=0.2
        )
        st.write("Resposta da IA:")
        st.write(response.choices[0].message.content)
