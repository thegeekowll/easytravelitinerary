"""
Azure Blob Storage service.

Handles file uploads, downloads, and management in Azure Blob Storage.
"""
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
try:
    from azure.storage.blob import BlobServiceClient, ContainerClient
    AZURE_AVAILABLE = True
except ImportError:
    BlobServiceClient = None
    ContainerClient = None
    AZURE_AVAILABLE = False
    print("Warning: azure-storage-blob not installed. Azure features disabled.")

from app.core.config import settings
import uuid


class AzureBlobService:
    """Service for Azure Blob Storage operations."""

    def __init__(self):
        """Initialize Azure Blob Service Client."""
        connection_string = settings.AZURE_STORAGE_CONNECTION_STRING

        # Check if connection string is valid (not empty, not placeholder)
        is_valid_connection = (
            AZURE_AVAILABLE and
            connection_string and
            connection_string.strip() and
            not connection_string.startswith("your-") and
            "AccountName=" in connection_string
        )

        if is_valid_connection:
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    connection_string
                )
            except Exception as e:
                print(f"Warning: Failed to initialize Azure Blob Storage: {e}")
                self.blob_service_client = None
        else:
            self.blob_service_client = None
            if settings.is_development:
                print("Azure Blob Storage not configured. Using placeholder URLs for development.")

    def _get_container_client(self, container_name: str) -> ContainerClient:
        """Get or create container client."""
        if not self.blob_service_client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Azure Blob Storage not configured"
            )

        container_client = self.blob_service_client.get_container_client(container_name)

        # Create container if it doesn't exist
        if not container_client.exists():
            container_client.create_container()

        return container_client

    async def upload_image(
        self,
        file: UploadFile,
        container: str,
        folder: str = ""
    ) -> str:
        """
        Upload an image file to Azure Blob Storage or Local Storage (dev).
        """
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
        
        # Determine blob name (or relative path)
        blob_name = f"{folder}/{unique_filename}" if folder else unique_filename

        if not self.blob_service_client:
            # Local Storage Fallback
            import os
            import aiofiles
            
            # Base uploads directory
            base_upload_dir = "/app/uploads"
            
            # Create container directory
            container_dir = os.path.join(base_upload_dir, container)
            if folder:
                container_dir = os.path.join(container_dir, folder)
                
            os.makedirs(container_dir, exist_ok=True)
            
            # Full local path
            file_path = os.path.join(container_dir, unique_filename)
            
            try:
                # Save file locally
                async with aiofiles.open(file_path, 'wb') as out_file:
                    content = await file.read()
                    await out_file.write(content)
                    
                # Return relative URL so it works behind nginx reverse proxy
                url = f"/uploads/{container}/{blob_name}"
                print(f"DEBUG: Local upload saved to {file_path}")
                print(f"DEBUG: Returning URL {url}")
                return url
                
            except Exception as e:
                print(f"Local upload failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload file locally: {str(e)}"
                )

        try:
            # Azure Upload Logic
            # Get container client
            container_client = self._get_container_client(container)

            # Upload file
            blob_client = container_client.get_blob_client(blob_name)
            await file.seek(0)
            content = await file.read()
            blob_client.upload_blob(content, overwrite=True)

            # Return URL
            return blob_client.url

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )

    def delete_image(self, blob_url: str) -> bool:
        """
        Delete an image from Azure Blob Storage or Local Storage (dev).
        """
        if not self.blob_service_client:
            # Local Storage Delete
            try:
                import os
                # Extract relative path from URL
                # Supports both absolute and relative URL formats
                
                if "/uploads/" not in blob_url:
                     return False
                     
                relative_path = blob_url.split("/uploads/")[1]
                file_path = os.path.join("/app/uploads", relative_path)
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True
                return False
                
            except Exception as e:
                print(f"Local delete failed: {e}")
                return False

        try:
            # Extract container and blob name from URL
            parts = blob_url.split('/')
            container_name = parts[-2]
            blob_name = parts[-1]

            container_client = self._get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.delete_blob()

            return True

        except Exception:
            return False

    def list_images(self, container: str, folder: str = "") -> List[str]:
        """
        List all images in a container/folder.

        Args:
            container: Container name
            folder: Optional folder path

        Returns:
            List[str]: List of blob URLs

        Example:
            images = azure_service.list_images(
                container="destinations",
                folder="paris"
            )
        """
        if not self.blob_service_client:
            return []  # Placeholder for development

        try:
            container_client = self._get_container_client(container)
            prefix = f"{folder}/" if folder else None

            blobs = container_client.list_blobs(name_starts_with=prefix)
            return [blob_client.url for blob in blobs]

        except Exception:
            return []

    async def upload_file_direct(
        self,
        file_content: bytes,
        filename: str,
        container: str,
        folder: str = "",
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Upload file content directly (without UploadFile wrapper).

        Args:
            file_content: Raw file bytes
            filename: Desired filename
            container: Container name
            folder: Optional folder path
            content_type: MIME type

        Returns:
            str: URL of uploaded file
        """
        if not self.blob_service_client:
            # For development without Azure, return placeholder
            return f"https://placeholder.com/{container}/{folder}/{filename}"

        try:
            # Construct blob name with folder path
            blob_name = f"{folder}/{filename}" if folder else filename

            # Get container client
            container_client = self._get_container_client(container)

            # Upload file
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(
                file_content,
                overwrite=True,
                content_settings={'content_type': content_type}
            )

            # Return URL
            return blob_client.url

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )


# Create singleton instance
azure_blob_service = AzureBlobService()
