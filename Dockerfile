FROM python:3.11-slim

WORKDIR /app

# install system dependencies untuk OpenCV & PIL
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libjpeg-dev \
    libpng-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# copy dependency dulu (biar caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy semua code
COPY . .

# port Cloud Run wajib 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]