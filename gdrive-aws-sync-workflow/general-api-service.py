import os
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
import uvicorn
from datetime import datetime
from pydantic import BaseModel
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class FolderItem(BaseModel):
    id: str
    name: str
    type: str
    mimeType: str
    modifiedTime: Optional[str] = None
    size: Optional[str] = None

class TransferStatus(BaseModel):
    status: str
    start_time: str
    end_time: Optional[str] = None
    stats: Optional[Dict] = None
    error: Optional[str] = None

class DriveService:
    SCOPES = [
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    def __init__(self, service_account_file: str):
        self.credentials = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=self.SCOPES
        )
        self.service = build("drive", "v3", credentials=self.credentials)

    def list_folders(self, parent_id: Optional[str] = None, query: Optional[str] = None) -> List[FolderItem]:
        try:
            # Base query for folders
            if query:
                base_query = f"mimeType = 'application/vnd.google-apps.folder' and name contains '{query}'"
            else:
                base_query = "mimeType = 'application/vnd.google-apps.folder'"
            
            # Add parent folder condition if specified
            if parent_id:
                base_query += f" and '{parent_id}' in parents"
            
            items = []
            page_token = None
            
            while True:
                results = self.service.files().list(
                    q=base_query,
                    spaces='drive',
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
                    pageToken=page_token,
                    pageSize=100
                ).execute()
                
                for item in results.get('files', []):
                    items.append(FolderItem(
                        id=item['id'],
                        name=item['name'],
                        type='folder',
                        mimeType=item['mimeType'],
                        modifiedTime=item.get('modifiedTime')
                    ))
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
                    
            return items
            
        except HttpError as error:
            raise HTTPException(status_code=500, detail=f"Google Drive API error: {str(error)}")

    def list_folder_contents(self, folder_id: str, file_types: Optional[List[str]] = None) -> List[FolderItem]:
        try:
            query = f"'{folder_id}' in parents"
            
            # Add file type filter if specified
            if file_types:
                mime_types = [f"mimeType = '{mime}'" for mime in file_types]
                query += f" and ({' or '.join(mime_types)})"
            
            items = []
            page_token = None
            
            while True:
                results = self.service.files().list(
                    q=query,
                    spaces='drive',
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
                    pageToken=page_token,
                    pageSize=100
                ).execute()
                
                for item in results.get('files', []):
                    item_type = 'folder' if item['mimeType'] == 'application/vnd.google-apps.folder' else 'file'
                    items.append(FolderItem(
                        id=item['id'],
                        name=item['name'],
                        type=item_type,
                        mimeType=item['mimeType'],
                        modifiedTime=item.get('modifiedTime'),
                        size=item.get('size')
                    ))
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
                    
            return items
            
        except HttpError as error:
            raise HTTPException(status_code=500, detail=f"Google Drive API error: {str(error)}")

    def get_folder_path(self, folder_id: str) -> List[Dict[str, str]]:
        try:
            path = []
            current_id = folder_id
            
            while current_id:
                try:
                    folder = self.service.files().get(
                        fileId=current_id,
                        fields="id, name, parents"
                    ).execute()
                    
                    path.insert(0, {
                        "id": folder["id"],
                        "name": folder["name"]
                    })
                    
                    # Get parent folder ID
                    current_id = folder.get("parents", [None])[0]
                    
                except HttpError as e:
                    if e.resp.status == 404:
                        break
                    raise
                    
            return path
            
        except HttpError as error:
            raise HTTPException(status_code=500, detail=f"Google Drive API error: {str(error)}")

app = FastAPI(title="Drive Explorer and Transfer API")

# Store running jobs and their status
jobs: Dict[str, TransferStatus] = {}

# Initialize Drive service
drive_service = None

@app.on_event("startup")
async def startup_event():
    global drive_service
    service_account_file = os.getenv('SERVICE_ACCOUNT_FILE', '/app/secrets/google-service-account.json')
    drive_service = DriveService(service_account_file)

@app.get("/")
async def root():
    return {"status": "alive", "service": "Drive Explorer and Transfer API"}

@app.get("/folders", response_model=List[FolderItem])
async def list_folders(
    parent_id: Optional[str] = None,
    query: Optional[str] = None
):
    """List folders in Google Drive. Optionally filter by parent folder or search query."""
    return drive_service.list_folders(parent_id, query)

@app.get("/folders/{folder_id}/contents", response_model=List[FolderItem])
async def get_folder_contents(
    folder_id: str,
    file_types: Optional[List[str]] = Query(None)
):
    """List contents of a specific folder."""
    return drive_service.list_folder_contents(folder_id, file_types)

@app.get("/folders/{folder_id}/path")
async def get_folder_path(folder_id: str):
    """Get the full path to a folder."""
    return drive_service.get_folder_path(folder_id)

@app.post("/transfer")
async def start_transfer(background_tasks: BackgroundTasks, folder_id: Optional[str] = None) -> Dict:
    """Start a transfer job for a specific folder or the default Dataset folder."""
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    jobs[job_id] = TransferStatus(
        status="starting",
        start_time=datetime.now().isoformat()
    )

    background_tasks.add_task(run_transfer, job_id, folder_id)
    
    return {
        "job_id": job_id,
        "status": "started",
        "message": "Transfer job started"
    }

@app.get("/status/{job_id}", response_model=TransferStatus)
async def get_status(job_id: str):
    """Get the status of a specific transfer job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.get("/jobs")
async def list_jobs():
    """List all transfer jobs."""
    return {"jobs": jobs}

async def run_transfer(job_id: str, folder_id: Optional[str] = None):
    try:
        jobs[job_id].status = "running"
        
        # Your existing transfer logic here
        # Use folder_id if provided, otherwise find Dataset folder
        
        jobs[job_id].status = "completed"
        jobs[job_id].end_time = datetime.now().isoformat()
        
    except Exception as e:
        jobs[job_id].status = "failed"
        jobs[job_id].end_time = datetime.now().isoformat()
        jobs[job_id].error = str(e)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
