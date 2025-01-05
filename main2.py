import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from pdf2image import convert_from_bytes
import os
from dotenv import load_dotenv
from io import BytesIO
import base64
import magic

# --- Configuração ---
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Chave da API não encontrada no arquivo .env.")
    st.stop()

client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL_ID = "gemini-2.0-flash-exp"  # Modelo multimodal

# --- Funções ---
def validate_file(file):
    """Valida o tipo de arquivo."""
    mime_type = magic.Magic(mime=True).from_buffer(file.getbuffer())
    if mime_type not in ["application/pdf", "image/png", "image/jpeg"]:
        raise ValueError(f"Tipo de arquivo não suportado: {mime_type}")
    return mime_type

def process_file(file):
    """Converte PDFs para imagens ou carrega imagens diretamente e processa."""
    try:
        mime_type = validate_file(file)
        images = []

        if mime_type == "application/pdf":
            # Converte PDF para uma lista de imagens
            pdf_bytes = BytesIO(file.getbuffer())
            images = convert_from_bytes(pdf_bytes.read())
        else:
            # Abre diretamente a imagem
            images.append(Image.open(file))

        if not images:
            raise RuntimeError("Nenhuma imagem encontrada no arquivo.")

        transcription = ""
        progress = st.progress(0)

        for index, image in enumerate(images):
            # Converte a imagem para base64
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            buffered.seek(0)
            image_base64 = base64.b64encode(buffered.read()).decode("utf-8")

            # Envia a imagem para a API
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[
                    image_base64,
                    (
                        "Transcreva na íntegra todo conteúdo da imagem fornecida, incluindo cabeçalhos, "
                        "rodapés, subtextos, imagens (com texto alternativo), tabelas e outros elementos."
                        "Requisitos: Retorne o conteúdo completo, sem explicações ou comentários adicionais."
                    ),
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
        with st.spinner("Processando..."):
            st.session_state.transcription = process_file(uploaded_file)

# Exibindo transcrição e opções
if st.session_state.transcription:
    st.markdown("### Texto Transcrito")
    st.text_area(" ", st.session_state.transcription, height=400)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Baixar Transcrição", st.session_state.transcription, file_name="transcricao.txt")
    with col2:
        if st.button("Nova Transcrição"):
            st.session_state.reset_transcription = True
