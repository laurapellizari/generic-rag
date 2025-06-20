import pandas as pd
import logging
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

embedding = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embedding_text(text, document_name):
  logging.info("embedding text...")

  splitter = RecursiveCharacterTextSplitter()

  splitter._chunk_size=2000
  splitter._chunk_overlap=250

  chunks = splitter.split_text(text)
  num_chunks = len(chunks)
  lista_vetor = []

  for i in range (num_chunks):
      lista_vetor.append(embedding.encode(chunks[i]))

  indexMapping = {
      "properties":{
          "Page":{
              "type":"text"
          },
          "PageVector":{
              "type":"dense_vector",
              "dims": 384,
              "index":True,
              "similarity": "cosine"
          },
          "DocumentName":{
              "type":"text"
          }
      }
  }

  list_docs = [document_name]*len(lista_vetor)

  my_dict = {
      "Page": chunks,
      "PageVector": lista_vetor,
      "DocumentName": list_docs
  }

  df = pd.DataFrame.from_dict(my_dict)

  text_embeddings_list = df.to_dict("records")

  return indexMapping, text_embeddings_list, num_chunks

def get_query_embedding(query: str):
    return embedding.encode(query)
