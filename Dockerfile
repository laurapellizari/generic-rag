FROM python:3.10-slim

WORKDIR /src

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /src/start.sh
EXPOSE 5000 8501

CMD ["sh", "start.sh"]
