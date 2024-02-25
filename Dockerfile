FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install necessary packages
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install required Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python script to the working directory
COPY sync_gdrive_to_s3.py .

ARG SERVICE_ACCOUNT_FILE

# Set the entrypoint to run the Python script
CMD ["python", "sync_gdrive_to_s3.py", "$service-account-file"]
```

