import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from pdf2image import convert_from_path
import os
from dotenv import load_dotenv

# --- Configuração ---
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Chave da API não encontrada no arquivo .env.")
    st.stop()

client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL_ID = "gemini-2.0-flash-exp"  # Modelo multimodal

# --- Funções ---
def process_file(file):
    """Converte PDFs para imagens ou carrega imagens diretamente."""
    try:
        images = []
        if file.name.endswith(".pdf"):
            # Converte PDF para uma lista de imagens
            with open(file.name, "wb") as f:
                f.write(file.getbuffer())
            images = convert_from_path(file.name)
        else:
            # Abre diretamente a imagem
            images.append(Image.open(file))

        if not images:
            raise RuntimeError("Nenhuma imagem encontrada no arquivo.")

        transcription = ""
        progress = st.progress(0)

        for index, image in enumerate(images):
            # Envia a imagem diretamente para a API
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[
                    image,
                    "Trancreva na integra todo conteudo da imagem fornecida."
                    "Certifique-se de que todo o conteúdo da página esteja incluído, como cabeçalhos,"
                    "rodapés, subtextos, imagens (com texto alternativo, se possível),"
                    "tabelas e quaisquer outros elementos."
                    "Requisitos: - retorne apenas o conteúdo sem quaisquer explicações ou comentários adicionais."
                    "Sem Delimitadores: Não use limites de código ou delimitadores."
                    "Conteúdo Completo: Não omita nenhuma parte da página, incluindo cabeçalhos, rodapés e subtexto.",
                ],
            )
            transcription += response.text + "\n"

            # Atualiza o progresso
            progress.progress((index + 1) / len(images))

        return transcription
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return None

# --- Interface do Streamlit ---
# Gerenciando estado do Streamlit
if "transcription" not in st.session_state:
    st.session_state.transcription = None
if "reset_transcription" not in st.session_state:
    st.session_state.reset_transcription = False

st.title("Conversor de PDF/Imagem para Texto")

# Reseta a transcrição se a flag estiver ativa
if st.session_state.reset_transcription:
    st.session_state.transcription = None
    st.session_state.reset_transcription = False

if st.session_state.transcription is None:
    # Upload de arquivo
    uploaded_file = st.file_uploader("Envie um arquivo PDF ou Imagem", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file:
        st.session_state.transcription = process_file(uploaded_file)

# Exibindo transcrição e opções
if st.session_state.transcription:
    st.markdown("### Texto Transcrito")
    st.text_area(" ", st.session_state.transcription, height=400)
    st.markdown("<style> .stTextArea { font-size: 16px; } </style>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("BAIXAR TRANSCRIÇÃO", st.session_state.transcription, file_name="transcricao.txt")
    with col2:
        if st.button("CLIQUE 2 VEZES PARA NOVA CONVERSÃO"):
            st.session_state.reset_transcription = True
    st.markdown("</div>", unsafe_allow_html=True)