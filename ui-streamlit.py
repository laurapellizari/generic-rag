import streamlit as st
import requests

API_BASE_URL = "http://localhost:5000"  # update this to match your actual Flask API URL

def api_list_documents(index):
    url = f"{API_BASE_URL}/list_docs"
    try:
        response = requests.get(url, params={"index": index})
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def api_delete_document(index, doc_id):
    url = f"{API_BASE_URL}/delete_docs/{index}/{doc_id}"
    try:
        response = requests.delete(url)
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500


st.set_page_config(layout="wide")

def api_connect(endpoint, api_key):
    url = f"{API_BASE_URL}/connect"
    payload = {
        "endpoint": endpoint,
        "api_key": api_key
    }
    try:
        response = requests.post(url, json=payload)
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def api_upload_documents(files):
    url = f"{API_BASE_URL}/documents"
    files_to_send = [("files", (file.name, file.getbuffer(), "application/pdf")) for file in files]
    try:
        response = requests.post(url, files=files_to_send)
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def api_search_question(index, question):
    url = f"{API_BASE_URL}/question"
    payload = {
        "index": index,
        "question": question
    }
    try:
        response = requests.post(url, json=payload)
        return response.json(), response.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# Session state for connection status
if "connected" not in st.session_state:
    st.session_state.connected = False

tab1, tab2, tab3, tab4 = st.tabs(['Connection', 'Upload Documents', 'Manage Indices', 'Search Content'])

with tab1:
    st.header("Connection Settings")

    with st.form(key="form_connection"):
        st.subheader("Elasticsearch Connection")
        endpoint = st.text_input("Elasticsearch Endpoint")
        api_key = st.text_input("API Key - Elasticsearch", type="password")

        st.subheader("LLM Provider")
        llm_provider = st.selectbox("Choose LLM Provider", ["OpenAI - gpt-4.1"])

        llm_api_key = st.text_input("LLM API Key", type="password")


        connect = st.form_submit_button("Connect")

        if connect:
            # Elasticsearch connection
            es_resp_json, es_status = api_connect(endpoint, api_key)
            if es_status == 200:
                st.session_state.connected = True
                st.success(es_resp_json.get("message", "Successfully connected to Elasticsearch!"))
            else:
                st.session_state.connected = False
                st.error(es_resp_json.get("error", "Elasticsearch connection failed."))

            st.session_state.llm_provider = llm_provider

            if llm_provider == "OpenAI - gpt-4.1":
                st.success("OpenAI API Key set.")
            else:
                st.warning("OpenAI API Key not provided.")

with tab2:
    st.header("Upload PDF Documents")

    if not st.session_state.connected:
        st.warning("Please connect to Elasticsearch first in the Connection tab.")
    else:
        uploaded_files = st.file_uploader("Select one or more PDF files", type=["pdf"], accept_multiple_files=True)

        if st.button("Upload Documents"):
            if uploaded_files:
                resp_json, status = api_upload_documents(uploaded_files)
                if status == 200:
                    st.success(f"{resp_json.get('message')}. Documents indexed: {resp_json.get('documents_indexed')}")
                else:
                    st.error(resp_json.get("error", "Failed to upload documents."))
            else:
                st.warning("Please upload at least one PDF file.")

with tab3:
    st.header("Manage Indices (List and Delete)")

    if not st.session_state.connected:
        st.warning("Please connect to Elasticsearch first in the Connection tab.")
    else:
        # índice hardcoded
        index_name = "company_xpto"

        if st.button("List Documents"):
            resp_json, status = api_list_documents(index_name)

            if status == 200:
                docs = resp_json.get("documents", [])

                if docs and isinstance(docs[0], dict):
                    # Remove documentos duplicados pelo nome
                    seen_names = set()
                    unique_docs = []

                    for doc in docs:
                        name = doc.get("_source", {}).get("DocumentName", "Unnamed")
                        if name not in seen_names:
                            seen_names.add(name)
                            unique_docs.append(doc)

                    st.subheader("Indexed Documents")

                    for i, doc in enumerate(unique_docs):
                        doc_id = doc.get("_id", f"doc_{i}")
                        name = doc.get("_source", {}).get("DocumentName", "Unnamed")

                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"- **{name}**")
                        with col2:
                            if st.button("Delete", key=f"delete_{doc_id}"):
                                del_resp, del_status = api_delete_document(index_name, doc_id)
                                if del_status == 200:
                                    st.success(f"Deleted: {name}")
                                else:
                                    st.error(f"Failed to delete: {name}")
                else:
                    st.warning("Nenhum documento encontrado ou resposta inesperada do backend.")
            else:
                st.error(resp_json.get("error", "Failed to retrieve documents."))


with tab4:
    st.header("Search Content")

    if not st.session_state.connected:
        st.warning("Please connect to Elasticsearch first in the Connection tab.")
    else:
        with st.form("form_search"):
            question = st.text_input("Query or Question")
            search = st.form_submit_button("Search")

            if search:
                if not question:
                    st.warning("Please provide a question.")
                else:
                    index = "company_xpto"  

                    payload = {
                        "question": question,
                        "openai_api_key": llm_api_key
                    }

                    response = requests.post("http://localhost:5000/question", json=payload)

                    if response.status_code == 200:
                        answer = response.json().get("answer", "No answer returned.")
                        st.markdown("### Answer:")
                        st.success(answer)
                    else:
                        error = response.json().get("error", "Error calling model.")
                        st.error(f"Error: {error}")
