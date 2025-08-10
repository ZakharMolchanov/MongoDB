FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Установка mongosh
RUN apt-get update && apt-get install -y curl gnupg \
    && curl -fsSL https://pgp.mongodb.com/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/mongodb-server.gpg] https://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org.list \
    && apt-get update && apt-get install -y mongodb-mongosh \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["python", "run.py"]
