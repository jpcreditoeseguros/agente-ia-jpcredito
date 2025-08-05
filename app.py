import streamlit as st
import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

st.title('Análise de Propostas de Crédito Habitação')

if 'processo' not in st.session_state:
    st.session_state['processo'] = None
if 'situacao_atual' not in st.session_state:
    st.session_state['situacao_atual'] = None
if 'propostas' not in st.session_state:
    st.session_state['propostas'] = []
if 'mais_propostas' not in st.session_state:
    st.session_state['mais_propostas'] = True
if 'dor' not in st.session_state:
    st.session_state['dor'] = None

# 1. Perguntar tipo de processo
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

# 2. Perguntar situação atual se aplicável
if st.session_state['processo'] == "Transferência de crédito habitação" and not st.session_state['situacao_atual']:
    with st.form("situacao_atual"):
        st.subheader("Situação atual")
        financiamento = st.text_input("Valor de financiamento (€)")
        prazo = st.text_input("Prazo em meses")
        seguros = st.text_input("Seguros (vida e/ou multirriscos, no banco ou fora)")
        prestacao = st.text_input("Prestação com seguros (€)")
        submeter = st.form_submit_button("Guardar situação atual")
    if submeter:
        st.session_state['situacao_atual'] = {
            "Valor de financiamento": financiamento,
            "Prazo em meses": prazo,
            "Seguros": seguros,
            "Prestação com seguros": prestacao
        }
        st.rerun()
    st.stop()

if st.session_state['processo'] == "Transferência de crédito habitação com reforço" and not st.session_state['situacao_atual']:
    with st.form("situacao_atual"):
        st.subheader("Situação atual")
        financiamento = st.text_input("Valor de financiamento (€)")
        prazo = st.text_input("Prazo em meses")
        seguros = st.text_input("Seguros (vida e/ou multirriscos, no banco ou fora)")
        prestacao = st.text_input("Prestação com seguros (€)")
        valor_outros_creditos = st.text_input("Valor com outros créditos (€)")
        prestacoes_outros_creditos = st.text_input("Prestações com outros créditos (€)")
        submeter = st.form_submit_button("Guardar situação atual")
    if submeter:
        st.session_state['situacao_atual'] = {
            "Valor de financiamento": financiamento,
            "Prazo em meses": prazo,
            "Seguros": seguros,
            "Prestação com seguros": prestacao,
            "Valor com outros créditos": valor_outros_creditos,
            "Prestações com outros créditos": prestacoes_outros_creditos
        }
        st.rerun()
    st.stop()

# 3. Adicionar propostas
if st.session_state['mais_propostas']:
    with st.form(key="adicionar_proposta"):
        st.subheader(f"Adicionar proposta {len(st.session_state['propostas'])+1}")
        banco = st.text_input("Nome do banco", key=f"banco{len(st.session_state['propostas'])}")
        financiamento = st.text_input("Valor de financiamento (€)", key=f"financiamento{len(st.session_state['propostas'])}")
        prazo = st.text_input("Prazo em meses", key=f"prazo{len(st.session_state['propostas'])}")
        
        # Campos por tipo de processo
        if st.session_state['processo'] in [
            "Transferência de crédito habitação com reforço", 
            "Crédito novo com reforço"
        ]:
            valor_reforco = st.text_input("Valor de reforço (€)", key=f"reforco{len(st.session_state['propostas'])}")
            valor_seguros = st.text_input("Valor de seguros (€)", key=f"seguros{len(st.session_state['propostas'])}")
            prestacao_total = st.text_input("Total de prestações com seguros (€)", key=f"prestacaototal{len(st.session_state['propostas'])}")
            custos = st.text_input("Custos associados (€)", key=f"custos{len(st.session_state['propostas'])}")
        else:
            prestacao = st.text_input("Prestação com seguros (€)", key=f"prestacao{len(st.session_state['propostas'])}")
            custos = st.text_input("Custos associados (€)", key=f"custos{len(st.session_state['propostas'])}")

        adicionar = st.form_submit_button("Adicionar proposta")

    if adicionar:
        if st.session_state['processo'] in [
            "Transferência de crédito habitação com reforço", 
            "Crédito novo com reforço"
        ]:
            st.session_state['propostas'].append({
                "Nome do banco": banco,
                "Valor de financiamento": financiamento,
                "Prazo em meses": prazo,
                "Valor de reforço": valor_reforco,
                "Valor de seguros": valor_seguros,
                "Total de prestações com seguros": prestacao_total,
                "Custos associados": custos
            })
        else:
            st.session_state['propostas'].append({
                "Nome do banco": banco,
                "Valor de financiamento": financiamento,
                "Prazo em meses": prazo,
                "Prestação com seguros": prestacao,
                "Custos associados": custos
            })
        st.rerun()

    if st.session_state['propostas']:
        st.markdown("#### Propostas já adicionadas:")
        for idx, p in enumerate(st.session_state['propostas']):
            st.write(f"Proposta {idx+1}: {p}")
        mais = st.radio(
            "Queres adicionar mais alguma proposta?",
            ("Sim", "Não"),
            key=f"mais_propostas_radio_{len(st.session_state['propostas'])}"
        )
        if mais == "Não":
            st.session_state['mais_propostas'] = False
            st.rerun()
        # Se sim, deixa continuar o ciclo normalmente

# 4. Perguntar dor do cliente
if not st.session_state['mais_propostas'] and not st.session_state['dor']:
    st.subheader("Motivo principal do cliente")
    dor = st.selectbox(
        "Qual a principal razão que levou o cliente a recorrer aos nossos serviços?",
        [
            "Preço",
            "Juntar vários créditos",
            "Valor mais alto de financiamento",
            "Seguros fora do banco",
            "Apenas mudar de banco",
            "Pedir valor de reforço"
        ]
    )
    if st.button("Confirmar motivo principal"):
        st.session_state['dor'] = dor
        st.rerun()
    st.stop()

# 5. Montar o prompt final e chamar a IA
if not st.session_state['mais_propostas'] and st.session_state['dor']:
    prompt = "Atua como um especialista em crédito habitação.\n\n"
    prompt += f"1. O processo é: {st.session_state['processo']}\n\n"

    # Situação atual se existir
    if st.session_state['situacao_atual']:
        prompt += "2. Situação atual:\n"
        for k, v in st.session_state['situacao_atual'].items():
            prompt += f"- {k}: {v}\n"
        prompt += "\n"

    prompt += "3. Propostas apresentadas:\n"
    for idx, p in enumerate(st.session_state['propostas']):
        prompt += f"Proposta {idx+1}:\n"
        for k, v in p.items():
            prompt += f"- {k}: {v}\n"
        prompt += "\n"

    prompt += f"4. Motivo principal que levou o cliente a procurar os nossos serviços: {st.session_state['dor']}\n\n"
    prompt += "---\n\n"
    prompt += "Análise:\n"
    prompt += "- Resume as condições de cada proposta e destaca as vantagens principais.\n"
    prompt += "- Compara as propostas apresentadas entre si, tendo em conta o motivo principal do cliente.\n"
    if st.session_state['processo'] in [
        "Transferência de crédito habitação", 
        "Transferência de crédito habitação com reforço"
    ]:
        prompt += "- Se o processo for transferência, analisa a poupança gerada entre a prestação com seguros das novas propostas e a situação atual.\n"
    prompt += "- Recomenda a proposta mais vantajosa para o objetivo do cliente, explicando porquê.\n"
    prompt += "- Dá sugestões para rebater possíveis objeções que possam surgir na apresentação da solução (por exemplo: custos iniciais, diferença de valor dos seguros, vantagens da mudança, etc.).\n\n"
    prompt += 'Termina SEMPRE com este texto:\n"Fico ao dispor para qualquer esclarecimento adicional ou para avançarmos com os próximos passos. 😊"\n'

    st.subheader("Prompt para IA (pré-visualização)")
    st.code(prompt)

    if st.button("Analisar propostas com IA"):
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
