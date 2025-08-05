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

    # Prompt dinâmico e verificação da coluna "Situação Atual"
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
            Se existir uma coluna “Situação Atual”, trata-se de uma transferência de crédito habitação — deves:
            - Realçar as melhorias e poupança gerada;
            - Fazer comparação clara entre situação atual e nova(s) proposta(s);
            - Destacar vantagens que o cliente vai sentir no dia a dia.
            """
        else:
            comparacao = """
            Neste caso, NÃO existe coluna “Situação Atual”, por isso NÃO faças qualquer referência a transferências, comparações com condições atuais, nem poupanças face ao passado.
            O foco é analisar e defender as propostas como crédito habitação para compra, construção ou hipotecário novo.
            """

        prompt = f"""
        Atua como um especialista em crédito habitação.
        O teu objetivo é analisar a folha 'Mapa comparativo' e ajudar o gestor a defender as várias propostas junto do cliente.
        Primeiro, considera que a principal dor do cliente é: **{dor_principal}**.

        Dá especial atenção aos seguintes critérios técnicos em cada proposta:
        - Montante de financiamento;
        - Prazo do empréstimo;
        - Prestação com seguros incluídos;
        - Valores dos seguros, especificando se são contratados dentro ou fora do banco;
        - Valor total dos custos associados com o processo de crédito.

        Com base nisto, deves:
        - Identificar a proposta mais vantajosa para a dor do cliente (p.ex. menor prestação, consolidação, retirar produtos obrigatórios, etc.);
        - Destacar benefícios claros e tangíveis da proposta escolhida;
        - Preparar argumentos de defesa para apresentar ao cliente, rebatendo objeções comuns.
        {comparacao}
        No final, sugere sempre uma frase de fecho para incentivar o cliente a avançar para a formalização.
        Usa linguagem simples, convincente e segura.
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
