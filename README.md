# Conversor de PDF/Imagem para Texto com Streamlit e Google GenAI

## 📋 Sobre o Projeto

Este projeto é um aplicativo interativo desenvolvido com **Streamlit**, que permite aos usuários fazer upload de arquivos PDF ou imagens e obter o texto contido nesses arquivos. Ele utiliza a API do **Google GenAI** (modelo Gemini 2.0) para realizar a transcrição do conteúdo. O sistema suporta processamento multimodal e é ideal para extrair texto de documentos complexos, como contratos, relatórios ou imagens com texto embutido.

---

## 🚀 Funcionalidades Principais

### ✅ **Upload de Arquivos**
- Aceita arquivos no formato **PDF** e **imagens** (PNG, JPG, JPEG).

### ✅ **Processamento Automático**
- Converte PDFs para imagens e processa cada página.
- Lê diretamente imagens enviadas para transcrição.

### ✅ **Transcrição Completa**
- Utiliza o modelo **Gemini 2.0** para garantir transcrições detalhadas de:
  - Cabeçalhos, rodapés, tabelas e subtextos.
  - Conteúdo textual em imagens complexas.

### ✅ **Barra de Progresso**
- Exibe o progresso do processamento em tempo real para melhor experiência do usuário.

### ✅ **Gerenciamento de Estado**
- Mantém a transcrição na sessão atual e permite reiniciar facilmente o processo.

### ✅ **Download do Resultado**
- Oferece um botão para baixar a transcrição como arquivo de texto.

---

## 🛠️ Tecnologias Utilizadas

### 📦 Bibliotecas Python
- **Streamlit**: Interface de usuário.
- **Pillow (PIL)**: Manipulação de imagens.
- **pdf2image**: Conversão de PDFs para imagens.
- **google-genai**: Integração com o modelo multimodal da Google.
- **dotenv**: Gerenciamento de variáveis de ambiente.

---

## 🏗️ Estrutura do Código

### **1. Configuração do Ambiente**
```python
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Chave da API não encontrada no arquivo .env.")
    st.stop()

client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL_ID = "gemini-2.0-flash-exp"  # Modelo multimodal
```
- Carrega as variáveis de ambiente do arquivo `.env`.
- Inicializa o cliente da API do Google GenAI.

### **2. Função de Processamento**
```python
def process_file(file):
    try:
        images = []
        if file.name.endswith(".pdf"):
            with open(file.name, "wb") as f:
                f.write(file.getbuffer())
            images = convert_from_path(file.name)
        else:
            images.append(Image.open(file))

        transcription = ""
        progress = st.progress(0)

        for index, image in enumerate(images):
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[
                    image,
                    "Trancreva na integra todo conteudo da imagem fornecida."
                ],
            )
            transcription += response.text + "\n"
            progress.progress((index + 1) / len(images))

        return transcription
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return None
```
- **Entrada**: Arquivo PDF ou imagem enviado pelo usuário.
- **Processamento**:
  - Converte PDFs em imagens com `pdf2image`.
  - Carrega imagens diretamente com `Pillow`.
- **API do Google GenAI**:
  - Envia imagens para transcrição utilizando o modelo Gemini 2.0.
- **Saída**: Retorna o texto transcrito.

### **3. Interface com Streamlit**
```python
if "transcription" not in st.session_state:
    st.session_state.transcription = None
if "reset_transcription" not in st.session_state:
    st.session_state.reset_transcription = False

st.title("Conversor de PDF/Imagem para Texto")

if st.session_state.reset_transcription:
    st.session_state.transcription = None
    st.session_state.reset_transcription = False

if st.session_state.transcription is None:
    uploaded_file = st.file_uploader("Envie um arquivo PDF ou Imagem", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file:
        st.session_state.transcription = process_file(uploaded_file)

if st.session_state.transcription:
    st.markdown("### Texto Transcrito")
    st.text_area(" ", st.session_state.transcription, height=400)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("BAIXAR TRANSCRIÇÃO", st.session_state.transcription, file_name="transcricao.txt")
    with col2:
        if st.button("CLIQUE 2 VEZES PARA NOVA CONVERSÃO"):
            st.session_state.reset_transcription = True
```
- Configura os estados da sessão para armazenar a transcrição.
- Gerencia o upload do arquivo e exibe os resultados.
- Oferece opções de download e reinicialização do processo.

---

## 🌟 Como Usar

1. **Clone este repositório**:
   ```bash
   git clone https://github.com/seu-usuario/conversor-pdf-imagem-texto.git
   cd conversor-pdf-imagem-texto
   ```

2. **Crie um ambiente virtual e instale as dependências**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure o arquivo `.env`**:
   - Crie um arquivo `.env` na raiz do projeto e adicione sua chave da API do Google:
     ```env
     GOOGLE_API_KEY=SuaChaveAPI
     ```

4. **Execute o aplicativo**:
   ```bash
   streamlit run app.py
   ```

5. **Acesse no navegador**:
   - O Streamlit abrirá automaticamente o aplicativo no navegador em `http://localhost:8501`.

---

## 📂 Estrutura do Projeto
```
.
├── app.py             # Código principal do aplicativo
├── requirements.txt   # Lista de dependências do Python
├── .env               # Configurações de variáveis de ambiente
├── README.md          # Este arquivo
```

---

## 🛡️ Contribuindo
Contribuições são bem-vindas! Siga os passos:

1. **Fork este repositório**.
2. Crie uma nova branch: `git checkout -b minha-nova-feature`.
3. Faça suas alterações e commit: `git commit -m 'Adicionei uma nova feature'`.
4. Envie para o GitHub: `git push origin minha-nova-feature`.
5. Abra um **Pull Request**.

---

## 📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 💬 Contato
Se tiver dúvidas ou sugestões, entre em contato:
- **Email**: carcalto@live.com
- **LinkedIn**: ([Celio Carcalto-LinkedIn](https://www.linkedin.com/in/celio-oliveira-car%C3%A7alto-908518142/))

---

✨ **Divirta-se utilizando o aplicativo!** 🚀

