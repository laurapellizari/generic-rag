#!/bin/sh

python app.py &

streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0
