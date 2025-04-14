# import streamlit as st
# import os
# from dotenv import load_dotenv
# from PyPDF2 import PdfReader

# from langchain.text_splitter import CharacterTextSplitter
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import FAISS
# from langchain.chat_models import ChatOpenAI
# from langchain.memory import ConversationBufferMemory
# from langchain.chains import ConversationalRetrievalChain

# from htmlTemplates import css, bot_template, user_template


# # --------------- Utility Functions -------------------

# def ensure_user_folder(username):
#     user_folder = os.path.join("uploads", username)
#     os.makedirs(user_folder, exist_ok=True)
#     return user_folder


# def save_uploaded_files(files, username):
#     user_folder = ensure_user_folder(username)
#     saved_paths = []

#     for file in files:
#         save_path = os.path.join(user_folder, file.name)
#         with open(save_path, "wb") as f:
#             f.write(file.read())
#         saved_paths.append(save_path)

#     return saved_paths


# def list_user_files(username):
#     user_folder = ensure_user_folder(username)
#     return [f for f in os.listdir(user_folder) if f.endswith(".pdf")]


# def get_pdf_text_from_paths(file_paths):
#     text = ""
#     for path in file_paths:
#         pdf_reader = PdfReader(path)
#         for page in pdf_reader.pages:
#             content = page.extract_text()
#             if content:
#                 text += content
#     return text


# def get_text_chunks(text):
#     text_splitter = CharacterTextSplitter(
#         separator="\n",
#         chunk_size=1000,
#         chunk_overlap=200,
#         length_function=len
#     )
#     return text_splitter.split_text(text)


# def get_vectorstore(text_chunks):
#     embeddings = OpenAIEmbeddings()
#     return FAISS.from_texts(texts=text_chunks, embedding=embeddings)


# def get_conversation_chain(vectorstore):
#     llm = ChatOpenAI()
#     memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
#     return ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=vectorstore.as_retriever(),
#         memory=memory
#     )


# def handle_userinput(user_question, username):
#     conversation_key = f"{username}_conversation"
#     chat_key = f"{username}_chat_history"

#     if st.session_state.get(conversation_key) is None:
#         st.warning("Please upload and process documents first.")
#         return

#     response = st.session_state[conversation_key]({'question': user_question})
#     st.session_state[chat_key] = response['chat_history']

#     for i, message in enumerate(st.session_state[chat_key]):
#         template = user_template if i % 2 == 0 else bot_template
#         st.write(template.replace("{{MSG}}", message.content), unsafe_allow_html=True)


# # ---------------- Main App -----------------------

# def main():
#     load_dotenv()
#     # st.set_page_config(page_title="Chit Chat", page_icon=":books:")  # Must be placed at top of script
#     st.write(css, unsafe_allow_html=True)

#     if "username" not in st.session_state:
#         st.warning("Please login first!")
#         return

#     username = st.session_state.username
#     conversation_key = f"{username}_conversation"
#     chat_key = f"{username}_chat_history"

#     if conversation_key not in st.session_state:
#         st.session_state[conversation_key] = None
#     if chat_key not in st.session_state:
#         st.session_state[chat_key] = None

#     st.header("Chit Chat :books:")
#     user_question = st.text_input("Ask a question about your documents:")

#     if user_question:
#         handle_userinput(user_question, username)

#     # ---------------- Sidebar -----------------------
#     with st.sidebar:
#         st.subheader(f"📂 Files for `{username}`")

#         # Show uploaded files for this user
#         user_files = list_user_files(username)
#         if user_files:
#             for file in user_files:
#                 st.markdown(f"- {file}")
#         else:
#             st.info("No files uploaded yet.")

#         st.divider()

#         st.subheader("Upload new files")
#         pdf_docs = st.file_uploader(
#             "Upload your PDFs here and click on 'Process'",
#             accept_multiple_files=True,
#             key="file_uploader"
#         )

#         if st.button("Process") and pdf_docs:
#             with st.spinner("Processing..."):
#                 file_paths = save_uploaded_files(pdf_docs, username)
#                 raw_text = get_pdf_text_from_paths(file_paths)
#                 text_chunks = get_text_chunks(raw_text)
#                 vectorstore = get_vectorstore(text_chunks)

#                 # Save conversation chain and reset chat
#                 st.session_state[conversation_key] = get_conversation_chain(vectorstore)
#                 st.session_state[chat_key] = []


# if __name__ == '__main__':
#     main()


import streamlit as st
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader

from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from htmlTemplates import css, bot_template, user_template

# ---------------- Load API Key ----------------
load_dotenv()  # Only used in local dev

openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

if not openai_api_key:
    st.error("❌ OPENAI_API_KEY not found! Please set it in Streamlit Secrets or .env file.")
    st.stop()

# --------------- Utility Functions -------------------

def ensure_user_folder(username):
    user_folder = os.path.join("uploads", username)
    os.makedirs(user_folder, exist_ok=True)
    return user_folder


def save_uploaded_files(files, username):
    user_folder = ensure_user_folder(username)
    saved_paths = []

    for file in files:
        save_path = os.path.join(user_folder, file.name)
        with open(save_path, "wb") as f:
            f.write(file.read())
        saved_paths.append(save_path)

    return saved_paths


def list_user_files(username):
    user_folder = ensure_user_folder(username)
    return [f for f in os.listdir(user_folder) if f.endswith(".pdf")]


def get_pdf_text_from_paths(file_paths):
    text = ""
    for path in file_paths:
        pdf_reader = PdfReader(path)
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                text += content
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    return FAISS.from_texts(texts=text_chunks, embedding=embeddings)


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI(openai_api_key=openai_api_key)
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )


def handle_userinput(user_question, username):
    conversation_key = f"{username}_conversation"
    chat_key = f"{username}_chat_history"

    if st.session_state.get(conversation_key) is None:
        st.warning("Please upload and process documents first.")
        return

    response = st.session_state[conversation_key]({'question': user_question})
    st.session_state[chat_key] = response['chat_history']

    for i, message in enumerate(st.session_state[chat_key]):
        template = user_template if i % 2 == 0 else bot_template
        st.write(template.replace("{{MSG}}", message.content), unsafe_allow_html=True)


# ---------------- Main App -----------------------

def main():
    st.write(css, unsafe_allow_html=True)

    if "username" not in st.session_state:
        st.warning("Please login first!")
        return

    username = st.session_state.username
    conversation_key = f"{username}_conversation"
    chat_key = f"{username}_chat_history"

    if conversation_key not in st.session_state:
        st.session_state[conversation_key] = None
    if chat_key not in st.session_state:
        st.session_state[chat_key] = None

    st.header("Chit Chat :books:")
    user_question = st.text_input("Ask a question about your documents:")

    if user_question:
        handle_userinput(user_question, username)

    # ---------------- Sidebar -----------------------
    with st.sidebar:
        st.subheader(f"📂 Files for `{username}`")

        # Show uploaded files for this user
        user_files = list_user_files(username)
        if user_files:
            for file in user_files:
                st.markdown(f"- {file}")
        else:
            st.info("No files uploaded yet.")

        st.divider()

        st.subheader("Upload new files")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'",
            accept_multiple_files=True,
            key="file_uploader"
        )

        if st.button("Process") and pdf_docs:
            with st.spinner("Processing..."):
                file_paths = save_uploaded_files(pdf_docs, username)
                raw_text = get_pdf_text_from_paths(file_paths)
                text_chunks = get_text_chunks(raw_text)
                vectorstore = get_vectorstore(text_chunks)

                # Save conversation chain and reset chat
                st.session_state[conversation_key] = get_conversation_chain(vectorstore)
                st.session_state[chat_key] = []


if __name__ == '__main__':
    main()
