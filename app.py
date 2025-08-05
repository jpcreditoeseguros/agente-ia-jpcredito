import streamlit as st
import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

st.title('Análise Manual de Propostas de Crédito Habitação')

# Inicializar variáveis de sessão
if 'propostas' not in st.session_state:
    st.session_state['propostas'] = []
if 'processo' not in st.session_state:
    st.session_state['processo'] = None
if 'dor' not in st.session_state:
    st.session_state['dor'] = None
if 'situacao_atual' not in st.session_state:
    st.session_state['situacao_atual'] = {}

# 1. Seleção do tipo de processo
if not st.session_state['processo']:
    st.subheader("Tipo de processo")
    processo = st.selectbox(
        "Seleciona o tipo de processo:",
        [
            "Transferência de crédito habitação",
            "Transferência de crédito habitação com reforço",
            "Crédito novo",
            "Crédito novo com reforço"
        ]
    )
    if st.button("Confirmar tipo de processo"):
        st.session_state['processo'] = processo
       st.rerun()
    st.stop()

# 2. Se for transferência, pedir dados da situação atual
if st.session_state['processo'] in ["Transferência de crédito habitação", "Transferência de crédito habitação com reforço"] and not st.session_state['situacao_atual']:
    with st.form("situacao_atual"):
        st.subheader("Situação atual")
        valor_financiamento = st.text_input("Valor de financiamento atual (€)")
        prazo_atual = st.text_input("Prazo restante (meses)")
        tipo_taxa = st.text_input("Tipo de taxa")
        valor_avaliacao = st.text_input("Valor de avaliação do imóvel (€)")
        tan_atual = st.text_input("TAN bonificada atual (%)")
        prestacao_atual = st.text_input("Prestação atual com seguros (€)")
        seguro_vida_atual = st.text_input("Valor do seguro de vida (€)")
        seguro_multi_atual = st.text_input("Valor do seguro multirriscos do imóvel (€)")
        valor_outros_creditos = st.text_input("Valor em dívida noutros créditos (€)")
        prestacoes_outros_creditos = st.text_input("Prestações mensais de outros créditos (€)")
        submeter_situacao = st.form_submit_button("Guardar situação atual")
    if submeter_situacao:
        st.session_state['situacao_atual'] = {
            'valor_financiamento': valor_financiamento,
            'prazo_atual': prazo_atual,
            'tipo_taxa': tipo_taxa,
            'valor_avaliacao': valor_avaliacao,
            'tan_atual': tan_atual,
            'prestacao_atual': prestacao_atual,
            'seguro_vida_atual': seguro_vida_atual,
            'seguro_multi_atual': seguro_multi_atual,
            'valor_outros_creditos': valor_outros_creditos,
            'prestacoes_outros_creditos': prestacoes_outros_creditos
        }
        st.experimental_rerun()
    st.stop()

# 3. Adição de propostas de acordo com o tipo de processo
with st.form(key='formulario_banco'):
    st.subheader(f"Proposta {len(st.session_state['propostas']) + 1}")
    banco = st.text_input("Nome do banco", key=f"banco{len(st.session_state['propostas'])}")
    montante = st.text_input("Montante financiado (€)", key=f"montante{len(st.session_state['propostas'])}")
    prazo = st.text_input("Prazo (meses)", key=f"prazo{len(st.session_state['propostas'])}")
    valor_avaliacao = st.text_input("Valor mínimo de avaliação (€)", key=f"aval{len(st.session_state['propostas'])}")
    tipo_taxa = st.text_input("Tipo de taxa", key=f"taxa{len(st.session_state['propostas'])}")
    tan = st.text_input("TAN bonificada (%)", key=f"tan{len(st.session_state['propostas'])}")
    # Campos para reforço
    valor_reforco = ""
    prazo_reforco = ""
    if st.session_state['processo'] in ["Transferência de crédito habitação com reforço", "Crédito novo com reforço"]:
        valor_reforco = st.text_input("Valor de reforço (€)", key=f"reforco{len(st.session_state['propostas'])}")
        prazo_reforco = st.text_input("Prazo do reforço (meses)", key=f"prazo_reforco{len(st.session_state['propostas'])}")
    # Seguros com escolha dentro/fora do banco
    seguro_vida = st.text_input("Seguro de Vida (€ e se é dentro/fora do banco)", key=f"vida{len(st.session_state['propostas'])}")
    seguro_multi = st.text_input("Seguro Multirriscos (€ e se é dentro/fora do banco)", key=f"multi{len(st.session_state['propostas'])}")
    # Prestação e custos
    if st.session_state['processo'] in ["Transferência de crédito habitação com reforço", "Crédito novo com reforço"]:
        prestacao = st.text_input("Total de prestações com seguros (€)", key=f"prestacao{len(st.session_state['propostas'])}")
    else:
        prestacao = st.text_input("Prestação com seguros (€)", key=f"prestacao{len(st.session_state['propostas'])}")
    custos = st.text_input("Custos associados (€)", key=f"custos{len(st.session_state['propostas'])}")
    adicionar = st.form_submit_button("Adicionar proposta")

if adicionar:
    st.session_state['propostas'].append({
        'banco': banco,
        'montante': montante,
        'prazo': prazo,
        'valor_avaliacao': valor_avaliacao,
        'tipo_taxa': tipo_taxa,
        'tan': tan,
        'valor_reforco': valor_reforco,
        'prazo_reforco': prazo_reforco,
        'seguro_vida': seguro_vida,
        'seguro_multi': seguro_multi,
        'prestacao': prestacao,
        'custos': custos
    })
    st.experimental_rerun()

# 4. Mostra propostas adicionadas e pergunta pela dor do cliente (só 1x)
if st.session_state['propostas']:
    st.subheader("Propostas adicionadas")
    for idx, prop in enumerate(st.session_state['propostas']):
        st.markdown(
            f"""
            **Proposta {idx+1}: {prop['banco']}**
            - Montante financiado: {prop['montante']}
            - Prazo: {prop['prazo']} meses / {round(float(prop['prazo'])/12, 1) if prop['prazo'].replace(' ','').isdigit() else 'N/A'} anos
            - Valor mínimo de avaliação: {prop['valor_avaliacao']}
            - Tipo de taxa: {prop['tipo_taxa']}
            - TAN bonificada: {prop['tan']}
            - Valor de reforço: {prop['valor_reforco']}
            - Prazo do reforço: {prop['prazo_reforco']}
            - Seguro de vida: {prop['seguro_vida']}
            - Seguro multirriscos: {prop['seguro_multi']}
            - Prestação: {prop['prestacao']}
            - Custos associados: {prop['custos']}
            """
        )
    if not st.session_state['dor']:
        st.subheader("Qual a principal razão que levou o cliente a recorrer aos nossos serviços?")
        dor = st.selectbox(
            "Seleciona a principal dor:",
            [
                "Preço",
                "Juntar vários créditos",
                "Valor mais alto de financiamento",
                "Seguros fora do banco",
                "Apenas mudar de banco",
                "Pedir valor de reforço"
            ]
        )
        if st.button("Confirmar dor do cliente"):
            st.session_state['dor'] = dor
            st.experimental_rerun()

# 5. Análise com IA (só mostra botão se já houver propostas E dor definida)
if st.session_state['propostas'] and st.session_state['dor']:
    if st.button("Analisar propostas com IA"):
        prompt = f"""
        Atua como um especialista em crédito habitação.
        Tipo de processo: {st.session_state['processo']}
        Dor do cliente: {st.session_state['dor']}
        """
        if st.session_state['situacao_atual']:
            prompt += "\nSituação atual do cliente:\n"
            for k, v in st.session_state['situacao_atual'].items():
                prompt += f"- {k.replace('_',' ').capitalize()}: {v}\n"
        prompt += "\nPropostas apresentadas:\n"
        for idx, prop in enumerate(st.session_state['propostas']):
            prompt += f"""
            Proposta {idx+1}: {prop['banco']}
            - Montante financiado: {prop['montante']}
            - Prazo: {prop['prazo']} meses / {round(float(prop['prazo'])/12, 1) if prop['prazo'].replace(' ','').isdigit() else 'N/A'} anos
            - Valor mínimo de avaliação: {prop['valor_avaliacao']}
            - Tipo de taxa: {prop['tipo_taxa']}
            - TAN bonificada: {prop['tan']}
            """
            if st.session_state['processo'] in ["Transferência de crédito habitação com reforço", "Crédito novo com reforço"]:
                prompt += f"- Valor de reforço: {prop['valor_reforco']}\n- Prazo do reforço: {prop['prazo_reforco']} meses\n"
            prompt += f"""- Seguro de vida: {prop['seguro_vida']}
            - Seguro multirriscos: {prop['seguro_multi']}
            - Prestação: {prop['prestacao']}
            - Custos associados: {prop['custos']}
            """

        prompt += """
        Analisa as propostas tendo em conta a dor apresentada e recomenda a melhor opção.
        Resume os principais pontos de cada proposta.
        Justifica a tua escolha e apresenta argumentos comerciais para defender a solução recomendada, rebatendo possíveis objeções do cliente. Termina com uma frase de incentivo à formalização.
        Todos os valores monetários devem ser apresentados ao cêntimo, com separador de milhares por espaço e o símbolo € (ex: 2 020,18€). As taxas de juro devem aparecer com três casas decimais e o símbolo % (ex: 2,550%).
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
    st.info("Adiciona pelo menos uma proposta para análise e indica a principal dor do cliente para continuar.")

