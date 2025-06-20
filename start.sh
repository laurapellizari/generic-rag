#!/bin/sh

# Inicia o backend Flask
python app.py &

# Inicia o frontend Streamlit
streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0
