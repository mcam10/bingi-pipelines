# Building a Scalable Google Drive to S3 Transfer Service with FastAPI and Kubernetes

In today's cloud-native world, moving data between different storage services is a common requirement. This blog post walks through building a robust service that transfers files from Google Drive to AWS S3, complete with a RESTful API, Kubernetes deployment, and Traefik integration.

## The Problem

Imagine you have a dataset stored in Google Drive that needs to be continuously synced to AWS S3. You want:
- A reliable transfer mechanism
- API access for automation
- Scalable deployment
- Progress tracking
- Error handling
- Security

## Architecture Overview

![Architecture Diagram]

Our solution consists of several components:

1. **FastAPI Application**: Provides RESTful endpoints for transfer operations
2. **Background Tasks**: Handles long-running transfers asynchronously
3. **Kubernetes Deployment**: Manages scaling and reliability
4. **Traefik Integration**: Handles routing and SSL termination

## Implementation Details

### Core Transfer Logic

The transfer service is built around the `DriveToS3Transfer` class, which handles the actual file operations:

```python
@dataclass
class TransferStats:
    """Class to hold transfer statistics"""
    total_files: int = 0
    downloaded_files: int = 0
    uploaded_files: int = 0
    skipped_files: int = 0
    failed_files: int = 0

class DriveToS3Transfer:
    def __init__(self, service_account_file: str, bucket_name: str):
        self.bucket_name = bucket_name
        self.stats = TransferStats()
        self.drive_service = self._init_drive_service(service_account_file)
        self.s3_client = self._init_s3_client()
```

The class provides methods for:
- Authenticating with Google Drive
- Finding files in specified folders
- Downloading files to temporary storage
- Uploading to S3
- Tracking transfer statistics

### RESTful API

We expose the transfer functionality through a FastAPI application:

```python
@app.post("/transfer")
async def start_transfer(background_tasks: BackgroundTasks) -> Dict:
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    jobs[job_id] = {
        "status": "starting",
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "stats": None,
        "error": None
    }
    background_tasks.add_task(run_transfer, job_id)
    return {"job_id": job_id, "status": "started"}
```

The API provides endpoints for:
- Starting transfers
- Checking transfer status
- Listing all jobs
- Viewing transfer statistics

### Project Structure

The project follows a clean, modular structure:

```
project/
├── Dockerfile
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── transfer.py       # Transfer logic
│   └── config.py         # Configuration
└── kubernetes/
    └── manifests/
        ├── deployment.yaml
        ├── service.yaml
        └── ingressroute.yaml
```

## Deployment

### Docker Container

The service is containerized using Docker:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/app/
RUN mkdir -p /app/temp_downloads

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

We use Kubernetes for orchestration:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gdrive-s3-transfer
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: gdrive-s3-transfer
        image: gdrive-s3-transfer:latest
        ports:
        - containerPort: 8000
        volumeMounts:
          - name: google-service-account
            mountPath: /app/secrets
```

### Traefik Integration

Traefik handles external access:

```yaml
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: gdrive-s3-transfer
spec:
  entryPoints:
    - web
    - websecure
  routes:
    - match: Host(`transfer.yourdomain.com`) && PathPrefix(`/api`)
      kind: Rule
      services:
        - name: gdrive-s3-transfer
          port: 80
```

## Security Considerations

The service implements several security measures:

1. **Secrets Management**:
   - Google Service Account credentials stored as Kubernetes secrets
   - AWS credentials managed through environment variables
   - No sensitive information in code or images

2. **Access Control**:
   - API endpoints can be protected with authentication
   - Traefik handles SSL termination
   - Minimal container privileges

3. **Data Protection**:
   - Temporary files cleaned up after transfer
   - Secure communications with both Google and AWS
   - No persistent storage of sensitive data

## Using the Service

### Starting a Transfer

```bash
curl -X POST https://transfer.yourdomain.com/api/transfer
```

Response:
```json
{
    "job_id": "20250211_123456",
    "status": "started",
    "message": "Transfer job started"
}
```

### Checking Status

```bash
curl https://transfer.yourdomain.com/api/status/20250211_123456
```

Response:
```json
{
    "status": "completed",
    "start_time": "2025-02-11T12:34:56",
    "end_time": "2025-02-11T12:35:30",
    "stats": {
        "total_files": 100,
        "downloaded_files": 100,
        "uploaded_files": 100,
        "skipped_files": 0,
        "failed_files": 0
    }
}
```

## Future Improvements

Potential enhancements include:

1. **Scalability**:
   - Implement horizontal pod autoscaling
   - Add support for parallel transfers
   - Optimize memory usage for large files

2. **Monitoring**:
   - Add Prometheus metrics
   - Implement detailed logging
   - Create Grafana dashboards

3. **Features**:
   - Support for other cloud storage providers
   - File filtering and pattern matching
   - Scheduled transfers

## Conclusion

This project demonstrates how to build a production-ready service for transferring files between cloud storage providers. By leveraging modern tools like FastAPI, Kubernetes, and Traefik, we've created a scalable, maintainable, and secure solution.

The complete code is available on [GitHub](#), and contributions are welcome!

## Getting Started

To run this project locally:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gdrive-s3-transfer.git
cd gdrive-s3-transfer
```

2. Set up credentials:
```bash
# Create .env file
cp .env.example .env
# Add your credentials
```

3. Build and run:
```bash
docker build -t gdrive-s3-transfer:latest .
docker run -p 8000:8000 gdrive-s3-transfer:latest
```

For production deployment, follow the Kubernetes deployment instructions in the documentation.

---

*This project is licensed under the MIT License - see the LICENSE file for details.*