FROM python:3.10-slim

WORKDIR /app

# Instala dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código para dentro do container
COPY . .

# Permissões e portas
RUN chmod +x /app/start.sh
EXPOSE 5000 8501

# Usa shell compatível
CMD ["sh", "start.sh"]
