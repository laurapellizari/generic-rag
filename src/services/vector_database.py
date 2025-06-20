import logging
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, TransportError
from services.embeddings import get_query_embedding

def index_data(elastic_client, index_name, index_mapping, data):
    logging.info(f"Indexing data into Elasticsearch index '{index_name}'...")

    try:
        if not elastic_client.indices.exists(index=index_name):
            logging.info(f"Index '{index_name}' does not exist. Creating it...")
            elastic_client.indices.create(index=index_name, mappings=index_mapping)
            logging.info(f"Index '{index_name}' created successfully.")
        else:
            logging.info(f"Index '{index_name}' already exists. Proceeding to index documents.")
    except Exception as e: 
        logging.exception(e)
        return False

    failed = 0

    for i, record in enumerate(data, 1):
        try:
            elastic_client.index(index=index_name, document=record)
        except Exception as e: 
            failed += 1
            logging.exception(e)

    if failed > 0:
        logging.warning(f"{failed} documents failed to index.")
        return False

    logging.info("All documents indexed successfully.")
    return True


def retrieve_context(elastic_client, index_name, query, top_k=3):
    try:
        query_vector = get_query_embedding(query)
        body = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'PageVector') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            }
        }

        response = elastic_client.search(index=index_name, body=body)
        hits = response["hits"]["hits"]

        return [hit["_source"].get("Page", "") for hit in hits]

    except Exception as e:
        logging.exception("Erro na busca vetorial")
        return []
