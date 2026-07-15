import streamlit as st
import requests
import pandas as pd


st.set_page_config(page_title="Assistente Acadêmico Unoesc", page_icon="🎓", layout="wide")

API_URL = "http://localhost:8000"


if "token" not in st.session_state:
    st.session_state["token"] = None
if "mensagens" not in st.session_state:
    st.session_state["mensagens"] = []

# ==========================================
# TELA DE LOGIN
# ==========================================
def tela_login():
    st.title("🎓 Login - Assistente Unoesc")
    st.markdown("Por favor, faça login para acessar o sistema.")
    
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        
        resposta = requests.post(
            f"{API_URL}/token", 
            data={"username": usuario, "password": senha} 
        )
        
        if resposta.status_code == 200:
            st.session_state["token"] = resposta.json().get("access_token")
            st.success("Login realizado com sucesso!")
            st.rerun() 
        else:
            st.error("Usuário ou senha incorretos.")

# ==========================================
# TELA DO CHAT (RF09)
# ==========================================
def tela_chat():
    st.title("💬 Chat com a Inteligência Artificial")
    
    
    codigo_aluno = st.number_input("Seu Código de Aluno", min_value=1, step=1)
    
    
    for msg in st.session_state["mensagens"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    
    pergunta = st.chat_input("Digite sua dúvida acadêmica...")
    
    if pergunta:
        
        st.session_state["mensagens"].append({"role": "user", "content": pergunta})
        with st.chat_message("user"):
            st.markdown(pergunta)
        
        
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        payload = {"codigoAluno": codigo_aluno, "pergunta": pergunta}
        
       
        with st.spinner("Pensando..."):
            resposta_api = requests.post(f"{API_URL}/perguntar", json=payload, headers=headers)
            
            if resposta_api.status_code == 200:
                texto_resposta = resposta_api.json().get("resposta")
            else:
                texto_resposta = f"❌ Erro na API: {resposta_api.text}"
        
        
        st.session_state["mensagens"].append({"role": "assistant", "content": texto_resposta})
        with st.chat_message("assistant"):
            st.markdown(texto_resposta)

# ==========================================
# TELA DO DASHBOARD (RF08)
# ==========================================
def tela_dashboard():
    st.title("📊 Dashboard de Estatísticas")
    
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    
    with st.spinner("Carregando dados..."):
        resposta = requests.get(f"{API_URL}/estatisticas", headers=headers)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Perguntas Hoje", dados["perguntas_hoje"])
            col2.metric("Sem Resposta (Hoje)", dados["sem_resposta_hoje"])
            col3.metric("Tempo Médio de Resposta (s)", dados["tempo_medio_resposta_segundos"])
            
            st.divider()
            
            st.subheader("Perguntas por Aluno")
            if dados["perguntas_por_aluno"]:
                
                df = pd.DataFrame(dados["perguntas_por_aluno"])
                df = df.set_index("codigoAluno")
                st.bar_chart(df)
            else:
                st.info("Ainda não há dados suficientes para o gráfico.")
                
        else:
            st.error("Erro ao carregar as estatísticas. Verifique sua conexão com a API.")



    # ==========================================
    # TABELA DE DOCUMENTOS CADASTRADOS
    # ==========================================
    st.divider() 
    st.subheader("📚 Documentos Atuais na Base")
    
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    
    with st.spinner("Carregando documentos..."):
        resposta_lista = requests.get(f"{API_URL}/base-conhecimento", headers=headers)
        
        if resposta_lista.status_code == 200:
            dados_base = resposta_lista.json()
            
            if dados_base:
                df_base = pd.DataFrame(dados_base)
                

                df_base = df_base[["id", "categoria", "titulo", "conteudo"]]
                
              
                st.dataframe(df_base, use_container_width=True, hide_index=True)
            else:
                st.info("A base de conhecimento ainda está vazia. Adicione o primeiro documento acima!")
        else:
            st.error("Erro ao carregar a lista de documentos.")





# ==========================================
# TELA DA BASE DE CONHECIMENTO (ADMIN)
# ==========================================
def tela_base_conhecimento():
    st.title("📚 Administração da Base de Conhecimento")
    st.markdown("Adicione novos documentos e regras institucionais para a IA estudar.")
    
   
    with st.form("form_novo_conhecimento", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            titulo = st.text_input("Título do Documento")
        with col2:
            categoria = st.selectbox("Categoria", ["Secretaria", "Financeiro", "Acadêmico", "TI", "Outros"])
            
        conteudo = st.text_area("Conteúdo (Texto que a IA usará como base para responder)", height=200)
        
        submit = st.form_submit_button("Salvar na Base de Conhecimento")
        
        if submit:
            if not titulo or len(conteudo) < 10:
                st.warning("Por favor, preencha o título e forneça um conteúdo válido (mínimo 10 caracteres).")
            else:
                headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                payload = {
                    "titulo": titulo,
                    "conteudo": conteudo,
                    "categoria": categoria
                }
                
                with st.spinner("Salvando..."):
                    resposta = requests.post(f"{API_URL}/alimentar-base", json=payload, headers=headers)
                    
                    if resposta.status_code == 200:
                        st.success("✅ Documento salvo com sucesso! A IA já sabe responder sobre isso.")
                    else:
                        st.error(f"Erro ao salvar: {resposta.text}")

    # ==========================================
    # TABELA DE DOCUMENTOS CADASTRADOS
    # ==========================================
    st.divider() 
    st.subheader("📚 Documentos Atuais na Base")
    
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    
    with st.spinner("Carregando documentos..."):
        resposta_lista = requests.get(f"{API_URL}/base-conhecimento", headers=headers)
        
        if resposta_lista.status_code == 200:
            dados_base = resposta_lista.json()
            
            if dados_base:
                df_base = pd.DataFrame(dados_base)
                
                df_base = df_base[["id", "categoria", "titulo", "conteudo"]]
                
                st.dataframe(df_base, use_container_width=True, hide_index=True)
            else:
                st.info("A base de conhecimento ainda está vazia. Adicione o primeiro documento acima!")
        else:
            st.error("Erro ao carregar a lista de documentos.")

# ==========================================
# CONTROLE DE NAVEGAÇÃO
# ==========================================
if st.session_state["token"] is None:
    tela_login()
else:
    st.sidebar.title("Navegação")
    
    opcao = st.sidebar.radio("Escolha uma tela:", ["Chat", "Dashboard", "Base de Conhecimento"])
    
    if st.sidebar.button("Sair"):
        st.session_state["token"] = None
        st.session_state["mensagens"] = []
        st.rerun()

    
    if opcao == "Chat":
        tela_chat()
    elif opcao == "Dashboard":
        tela_dashboard()
    elif opcao == "Base de Conhecimento":
        tela_base_conhecimento()