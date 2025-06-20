from services.extract_text import extract_text_from_pdf
from services.embeddings import embedding_text
from services.vector_database import index_data
from flask import Flask, request, jsonify
import tempfile
import logging
from pathlib import Path
from elasticsearch import Elasticsearch
from openai import OpenAI

PORT = 5000
app = Flask(__name__)

index_name = "company_xpto"
elastic_client = None

@app.route("/connect", methods=["POST"])
def connect_elasticsearch():
    global elastic_client

    data = request.json
    endpoint = data.get("endpoint")
    api_key = data.get("api_key")

    if not all([endpoint, api_key]):
        return jsonify({"error": "Missing credentials"}), 400

    try:
        elastic_client = Elasticsearch(
            endpoint,
            api_key=api_key
        )

        if not elastic_client.ping():
            return jsonify({"error": "Failed to connect to Elasticsearch"}), 500

        return jsonify({"message": "Successfully connected!"}), 200

    except Exception as e:
        logging.exception("Connection failed.")
        return jsonify({"error": str(e)}), 500

@app.route("/list_docs", methods=["GET"])
def list_documents():
    try:
        results = elastic_client.search(index=index_name, body={"query": {"match_all": {}}}, size=1000)
        documents = results["hits"]["hits"]  # retorna lista completa para pegar _id e _source
        return jsonify({"documents": documents}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/delete_docs", methods=["DELETE"])
def delete_document():
    data = request.get_json()
    index = data.get("index")
    doc_id = data.get("id")
    try:
        elastic_client.delete(index=index, id=doc_id)
        return jsonify({"message": f"Document {doc_id} deleted."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/documents", methods=['POST'])
def handle_documents():
    global elastic_client

    if elastic_client is None:
        return jsonify({"error": "Connection failed. Try /connect"}), 400

    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    uploaded_files = request.files.getlist("files")

    if not uploaded_files:
        return jsonify({"error": "No files found in request"}), 400

    results = {}
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            output_dir = tmpdir_path / "output"

            for uploaded_file in uploaded_files:
                if uploaded_file.filename == "":
                    continue

                pdf_path = tmpdir_path / uploaded_file.filename
                uploaded_file.save(str(pdf_path))

                markdown = extract_text_from_pdf(pdf_path, output_dir)
                results[uploaded_file.filename] = markdown

                indexMapping, text_embeddings_list, num_chunks = embedding_text(text=markdown, document_name=uploaded_file.filename)

                index_data(elastic_client, index_name, indexMapping, text_embeddings_list)

        return jsonify({
            "message": "Documents processed successfully",
            "documents_indexed": len(results),
            "total_chunks": num_chunks  
        })

    except Exception as e:
        logging.exception("Erro ao processar PDFs")
        return jsonify({"error": str(e)}), 500


@app.route("/question", methods=["POST"])
def main():
    global elastic_client

    data = request.get_json()
    question = data.get("question")
    openai_api_key = data.get("openai_api_key")

    if not question:
        return jsonify({"error": "Missing question"}), 400
    if not openai_api_key:
        return jsonify({"error": "Missing OpenAI API key"}), 400
    if elastic_client is None:
        return jsonify({"error": "Elasticsearch not connected"}), 400

    try:
        from services.vector_database import retrieve_context 
        context_chunks = retrieve_context(elastic_client, index_name, question)
        context = "\n".join(context_chunks)
        print(context)
        full_prompt = f"""
        You are an assistant specialized in technical documents. Based on the information below, answer the question clearly and directly in Portuguese.  
        If the context includes an image, return the image64 code.  
        Context:  
        {context}  

        Question: {question}
        """

        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.5,
            max_tokens=500
        )

        answer = response.choices[0].message.content.strip()
        return jsonify(
            {"answer": answer,
            "references": context}
        ), 200

    except Exception as e:
        logging.exception("Erro ao processar pergunta")
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=PORT)
