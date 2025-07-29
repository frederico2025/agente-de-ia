
import streamlit as st
import requests
import fitz  # PyMuPDF para leitura de PDFs

# Configuração da página
st.set_page_config(page_title="Chatbot Jurídico - Defensoria Pública", layout="wide")

# Sidebar: API Key e seleções
st.sidebar.title("⚙️ Configurações")
api_key = st.sidebar.text_input("🔑 API Key da Groq", type="password", help="Cadastre-se em https://console.groq.com")
modelo = st.sidebar.selectbox("🧠 Modelo LLM", ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"])
pagina = st.sidebar.selectbox("📄 Página", ["Chatbot Jurídico", "Sumarizador Jurídico"])

# Função para chamada à Groq
def consultar_groq(prompt):
    if not api_key:
        return "⚠️ Informe sua API Key da Groq."
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": "Você é um assistente jurídico da Defensoria Pública, especializado em orientação para pessoas hipossuficientes."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        r = requests.post(url, headers=headers, json=payload)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Erro: {e}"

# Página 1: Chatbot Jurídico
if pagina == "Chatbot Jurídico":
    st.title("🤖 Assistente Jurídico da Defensoria Pública")
    st.markdown("Este chatbot usa a API do **Groq** com o modelo `llama3-70b-8192` para responder dúvidas jurídicas com precisão.")

    if "historico" not in st.session_state:
        st.session_state.historico = []

    pergunta = st.text_area("✍️ Escreva sua dúvida jurídica:")

    if st.button("Enviar"):
        if pergunta.strip():
            resposta = consultar_groq(pergunta)
            st.session_state.historico.append(("Usuário", pergunta))
            st.session_state.historico.append(("Assistente", resposta))
        else:
            st.warning("Digite uma pergunta antes de enviar.")

    for autor, texto in st.session_state.historico:
        icone = "👤" if autor == "Usuário" else "🧑‍⚖️"
        st.markdown(f"**{icone} {autor}:** {texto}")

# Página 2: Sumarizador Jurídico
elif pagina == "Sumarizador Jurídico":
    st.title("📄 Sumarizador Jurídico de Documentos")
    st.markdown("Envie um ou mais arquivos PDF ou TXT. Será gerado um **resumo jurídico individual** para cada documento.")

    arquivos = st.file_uploader("📎 Enviar arquivos", type=["pdf", "txt"], accept_multiple_files=True)

    if arquivos:
        for arquivo in arquivos:
            nome = arquivo.name
            tipo = arquivo.type
            conteudo = ""

            if tipo == "application/pdf":
                try:
                    doc = fitz.open(stream=arquivo.read(), filetype="pdf")
                    conteudo = "\n".join([page.get_text() for page in doc])
                except Exception as e:
                    st.error(f"Erro ao ler PDF: {e}")
                    continue
            elif tipo == "text/plain":
                conteudo = arquivo.read().decode("utf-8")

            if conteudo:
                st.markdown(f"---\n### 📘 Documento: `{nome}`")
                st.text_area("📝 Conteúdo Detectado", value=conteudo[:2000], height=150, key=nome)

                if st.button(f"🔍 Resumir `{nome}`", key=f"resumir_{nome}"):
                    prompt = f"Resuma juridicamente o seguinte texto com linguagem acessível:\n\n{conteudo[:8000]}"
                    resumo = consultar_groq(prompt)
                    st.success("✅ Resumo Jurídico:")
                    st.markdown(resumo)
            else:
                st.warning(f"⚠️ Arquivo `{nome}` sem conteúdo extraído.")
