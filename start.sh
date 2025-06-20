#!/bin/bash

# Start Flask API
python app.py &

# Start Streamlit UI
streamlit run ui-streamlit.py --server.port 8501 --server.address 0.0.0.0
