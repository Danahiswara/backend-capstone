FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get clean

# copy dependency dulu (biar caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy semua code
COPY . .

# port Cloud Run wajib 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]