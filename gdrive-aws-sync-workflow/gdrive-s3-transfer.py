import os
import io
import time
import logging
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

# Google Drive imports
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

# AWS imports
import boto3
from botocore.exceptions import ClientError

# Environment variables
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@dataclass
class TransferStats:
    """Class to track file transfer statistics"""
    total_files: int = 0
    downloaded_files: int = 0
    uploaded_files: int = 0
    skipped_files: int = 0
    failed_files: int = 0

class DriveToS3Transfer:
    """Handles file transfer from Google Drive to AWS S3"""
    
    # Google Drive API scopes
    SCOPES = [
        "https://www.googleapis.com/auth/drive.metadata",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.metadata.readonly"
    ]

    def __init__(self, service_account_file: str, bucket_name: str):
        """
        Initialize the transfer service.
        
        Args:
            service_account_file (str): Path to Google service account credentials file
            bucket_name (str): AWS S3 bucket name
        """
        load_dotenv()
        
        self.bucket_name = bucket_name
        self.stats = TransferStats()
        self.temp_dir = Path("temp_downloads")
        
        # Initialize Google Drive service
        self.drive_service = self._init_drive_service(service_account_file)
        
        # Initialize S3 client
        self.s3_client = self._init_s3_client()
        
        # Create temp directory if it doesn't exist
        self.temp_dir.mkdir(exist_ok=True)

    def _init_drive_service(self, service_account_file: str):
        """Initialize Google Drive service"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file, scopes=self.SCOPES
            )
            return build("drive", "v3", credentials=credentials)
        except Exception as e:
            raise Exception(f"Failed to initialize Google Drive service: {str(e)}")

    def _init_s3_client(self):
        """Initialize AWS S3 client"""
        try:
            return boto3.client(
                's3',
                aws_access_key_id=os.getenv('Accesskey'),
                aws_secret_access_key=os.getenv('Secretaccesskey'),
                region_name="us-east-1"
            )
        except Exception as e:
            raise Exception(f"Failed to initialize S3 client: {str(e)}")

    def get_dataset_folder_id(self) -> Optional[str]:
        """Find the 'Dataset' folder ID in Google Drive"""
        try:
            response = self.drive_service.files().list(
                pageSize=10,
                fields="files(id, name)",
                q="mimeType='application/vnd.google-apps.folder' and name='Dataset'"
            ).execute()
            
            files = response.get('files', [])
            return files[0]['id'] if files else None
            
        except HttpError as e:
            logging.error(f"Error finding Dataset folder: {str(e)}")
            return None

    def get_class_folders(self, dataset_id: str) -> List[dict]:
        """Get list of class folders within the dataset folder"""
        try:
            response = self.drive_service.files().list(
                q=f"'{dataset_id}' in parents",
                pageSize=50,
                fields="files(id, name)"
            ).execute()
            
            return response.get('files', [])
            
        except HttpError as e:
            logging.error(f"Error getting class folders: {str(e)}")
            return []

    def download_file(self, file_id: str, file_name: str) -> Optional[Path]:
        """Download a single file from Google Drive"""
        temp_path = self.temp_dir / file_name
        
        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            
            with open(temp_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
            
            self.stats.downloaded_files += 1
            return temp_path
            
        except Exception as e:
            logging.error(f"Error downloading {file_name}: {str(e)}")
            if temp_path.exists():
                temp_path.unlink()
            return None

    def upload_to_s3(self, file_path: Path, s3_key: str) -> bool:
        """Upload a file to S3"""
        try:
            # Check if file already exists in S3
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
                logging.info(f"File already exists in S3: {s3_key}")
                self.stats.skipped_files += 1
                return True
            except ClientError as e:
                if e.response['Error']['Code'] not in ('404', 'NoSuchKey'):
                    raise

            # Upload file to S3
            self.s3_client.upload_file(str(file_path), self.bucket_name, s3_key)
            self.stats.uploaded_files += 1
            return True
            
        except Exception as e:
            logging.error(f"Error uploading to S3: {s3_key}: {str(e)}")
            self.stats.failed_files += 1
            return False

    def process_class_folder(self, folder: dict) -> None:
        """Process all images in a class folder"""
        try:
            # Get all files in the class folder
            response = self.drive_service.files().list(
                q=f"'{folder['id']}' in parents",
                pageSize=100,
                fields="files(id, name)"
            ).execute()
            
            files = response.get('files', [])
            self.stats.total_files += len(files)
            
            for file in files:
                logging.info(f"Processing {file['name']} in {folder['name']}")
                
                # Download file
                temp_path = self.download_file(file['id'], file['name'])
                if not temp_path:
                    self.stats.failed_files += 1
                    continue
                
                # Upload to S3
                s3_key = f"{folder['name']}/{file['name']}"
                self.upload_to_s3(temp_path, s3_key)
                
                # Clean up temp file
                temp_path.unlink()
                
        except Exception as e:
            logging.error(f"Error processing folder {folder['name']}: {str(e)}")

    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir.exists():
                for file in self.temp_dir.iterdir():
                    file.unlink()
                self.temp_dir.rmdir()
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")

    def transfer_files(self) -> bool:
        """Main method to transfer files from Google Drive to S3"""
        start_time = time.time()
        success = False
        
        try:
            # Get Dataset folder ID
            dataset_id = self.get_dataset_folder_id()
            if not dataset_id:
                logging.error("Could not find Dataset folder")
                return False
            
            # Get class folders
            class_folders = self.get_class_folders(dataset_id)
            if not class_folders:
                logging.error("No class folders found")
                return False
            
            # Process each class folder
            for folder in class_folders:
                logging.info(f"Processing folder: {folder['name']}")
                self.process_class_folder(folder)
            
            success = True
            
        except Exception as e:
            logging.error(f"Transfer failed: {str(e)}")
            
        finally:
            # Print statistics
            elapsed_time = time.time() - start_time
            logging.info("\nTransfer Summary:")
            logging.info(f"Total files found: {self.stats.total_files}")
            logging.info(f"Files downloaded: {self.stats.downloaded_files}")
            logging.info(f"Files uploaded: {self.stats.uploaded_files}")
            logging.info(f"Files skipped: {self.stats.skipped_files}")
            logging.info(f"Files failed: {self.stats.failed_files}")
            logging.info(f"Total time: {elapsed_time:.2f} seconds")
            
            # Cleanup
            self.cleanup()
            
        return success

def main():
    # Load environment variables
    load_dotenv()
    
    # Get required environment variables
    service_account_file = os.getenv('SERVICE_ACCOUNT_FILE')
    bucket_name = os.getenv('BUCKET_NAME', 'project-chocolate')
    
    if not service_account_file:
        logging.error("SERVICE_ACCOUNT_FILE environment variable not set")
        return 1
    
    try:
        # Initialize and run transfer
        transfer = DriveToS3Transfer(service_account_file, bucket_name)
        success = transfer.transfer_files()
        
        return 0 if success else 1
        
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())