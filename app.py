import streamlit as st
import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

st.title('Análise Manual de Propostas de Crédito Habitação')

if 'propostas' not in st.session_state:
    st.session_state['propostas'] = []

with st.form(key='formulario_banco'):
    st.subheader(f"Proposta {len(st.session_state['propostas']) + 1}")
    banco = st.text_input("Nome do banco", key=f"banco{len(st.session_state['propostas'])}")
    montante = st.text_input("Montante financiado (€)", value="66 938,00€", key=f"montante{len(st.session_state['propostas'])}")
    prazo = st.text_input("Prazo (meses)", value="240", key=f"prazo{len(st.session_state['propostas'])}")
    prestacao = st.text_input("Prestação com seguros (€)", value="376,31€", key=f"prestacao{len(st.session_state['propostas'])}")
    seguro_vida = st.text_input("Seguro de Vida (valor e se é dentro/fora do banco)", value="4,97€ fora do banco", key=f"vida{len(st.session_state['propostas'])}")
    seguro_multi = st.text_input("Seguro Multirriscos (valor e se é dentro/fora do banco)", value="15,00€ no banco", key=f"multi{len(st.session_state['propostas'])}")
    tan = st.text_input("TAN bonificada (%)", value="2,550%", key=f"tan{len(st.session_state['propostas'])}")
    taxa = st.text_input("Tipo de taxa", value="FIXA 3 ANOS", key=f"taxa{len(st.session_state['propostas'])}")
    custos = st.text_input("Custos associados (€)", value="2 020,18€", key=f"custos{len(st.session_state['propostas'])}")
    adicionar = st.form_submit_button("Adicionar proposta")

if adicionar:
    st.session_state['propostas'].append({
        'banco': banco,
        'montante': montante,
        'prazo': prazo,
        'prestacao': prestacao,
        'seguro_vida': seguro_vida,
        'seguro_multi': seguro_multi,
        'tan': tan,
        'taxa': taxa,
        'custos': custos
    })
    st.experimental_rerun()

if st.session_state['propostas']:
    st.subheader("Propostas adicionadas")
    for idx, prop in enumerate(st.session_state['propostas']):
        st.markdown(
            f"""
            **Proposta {idx+1}: {prop['banco']}**
            - Montante financiado: {prop['montante']}
            - Prazo: {prop['prazo']} meses / {round(float(prop['prazo'])/12, 1) if prop['prazo'].replace(' ','').isdigit() else 'N/A'} anos
            - Prestação com seguros: {prop['prestacao']}
            - Seguro de vida: {prop['seguro_vida']}
            - Seguro multirriscos: {prop['seguro_multi']}
            - TAN bonificada: {prop['tan']}
            - Tipo de taxa: {prop['taxa']}
            - Custos associados: {prop['custos']}
            """
        )
    if st.button("Analisar propostas com IA"):
        prompt = f"""
        Atua como um especialista em crédito habitação.
        Vais analisar várias propostas detalhadas abaixo.
        Para cada proposta, faz um resumo dos principais pontos (montante financiado, prazo, prestação com seguros, seguro de vida, seguro multirriscos, TAN bonificada, tipo de taxa, custos associados).
        Todos os valores monetários devem ser apresentados ao cêntimo, com separador de milhares por espaço e o símbolo € (ex: 2 020,18€). As taxas de juro devem aparecer com três casas decimais e o símbolo % (ex: 2,550%).
        Compara as propostas entre si e identifica qual a mais vantajosa, explicando porquê.
        No final, apresenta argumentos comerciais para defender a solução recomendada ao cliente, rebatendo objeções comuns, e termina com uma frase de fecho para incentivar à formalização.

        Propostas:
        """
        for idx, prop in enumerate(st.session_state['propostas']):
            prompt += f"""
            Proposta {idx+1}: {prop['banco']}
            - Montante financiado: {prop['montante']}
            - Prazo: {prop['prazo']} meses / {round(float(prop['prazo'])/12, 1) if prop['prazo'].replace(' ','').isdigit() else 'N/A'} anos
            - Prestação com seguros: {prop['prestacao']}
            - Seguro de vida: {prop['seguro_vida']}
            - Seguro multirriscos: {prop['seguro_multi']}
            - TAN bonificada: {prop['tan']}
            - Tipo de taxa: {prop['taxa']}
            - Custos associados: {prop['custos']}
            """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Responder como um gestor de crédito experiente."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1800,
            temperature=0.2
        )
        st.subheader("Resposta da IA:")
        st.write(response.choices[0].message.content)
    st.write("Queres adicionar outra proposta? Preenche os campos acima e carrega em 'Adicionar proposta'.")
else:
    st.info("Adiciona pelo menos uma proposta para análise.")
