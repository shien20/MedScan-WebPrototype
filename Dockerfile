FROM python:3.11-slim

WORKDIR /app

# System packages needed by OpenCV / image processing libraries
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    git-lfs \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# Hugging Face Spaces default port is usually 7860
ENV PORT=7860

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]