FROM python:3.12-slim

WORKDIR /app

# Install build dependencies for chroma-hnswlib and curl for healthcheck
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Install dependencies first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Generate the heritage PDF during build
RUN python generate_pdf.py

# Create directories for generated files
RUN mkdir -p static/audio chroma_data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
