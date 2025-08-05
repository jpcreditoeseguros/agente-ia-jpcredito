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
        Usa sempre os campos exatamente como aparecem na tabela seguinte, sem inventar, traduzir ou alterar nomes.
        Para cada banco, responde campo a campo, usando só os dados visíveis.

        Para cada proposta apresentada, responde sempre indicando:

        - Nome do banco (exatamente como está na tabela)
        - Montante financiado (apresenta sempre com separador de milhares por espaço, duas casas decimais e o símbolo €, ex: 66 938,00€)
        - Prazo (apresenta o número de meses E a conversão para anos, ex: 240 meses / 20 anos)
        - Prestação com seguros (sempre com separador de milhares por espaço, duas casas decimais e €, ex: 1 376,31€)
        - Para TODOS os campos de seguros presentes na tabela (como “Seguro de Vida Fora do Banco”, “Seguro Multirriscos Banco”, etc.), apresenta:
            - O nome exato do campo (não resumas, nem traduzes)
            - O valor (sempre com separador de milhares por espaço, duas casas decimais e €)
            - Especifica sempre se é dentro ou fora do banco, conforme o nome do campo
          NUNCA ignores nem resumas qualquer campo de seguros: apresenta todos os que existirem na tabela, um a um, para cada banco.
        - TAN bonificada (apresenta sempre como percentagem com três casas decimais e o símbolo %, ex: 3,550%)
        - Tipo de taxa
        - Custos associados (valor total com separador de milhares por espaço, duas casas decimais e €, ex: 2 020,18€)
        - Situação atual (se existir)
        Se algum campo não existir, diz “não consta na tabela”.

        Garante que todos os valores monetários são apresentados ao cêntimo (duas casas decimais), com separador de milhares por espaço, e que todas as taxas aparecem como percentagem com três casas decimais e o símbolo %.

        {comparacao}

        No final, identifica qual a proposta mais vantajosa para a dor do cliente, prepara argumentos claros para defender essa solução junto do cliente, antecipando e rebatendo objeções comuns.

        Termina sempre com uma frase de fecho forte, a incentivar o cliente a avançar para a formalização.

        Tabela de dados (transposta):
        {df.T.to_string()}
        """

    if st.button("Obter análise IA"):
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Responder como um gestor de crédito experiente."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1800,
            temperature=0.2
        )
        st.write("Resposta da IA:")
        st.write(response.choices[0].message.content)
