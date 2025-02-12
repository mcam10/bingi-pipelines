FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libheif-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the converter script
COPY heic_converter.py .

# Create directory for input/output
RUN mkdir -p /app/data

# Set entrypoint
ENTRYPOINT ["python", "heic_converter.py"]
