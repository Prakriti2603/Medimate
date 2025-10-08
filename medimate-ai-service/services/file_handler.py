"""
File handling utilities for document storage and management.
"""

import logging
import os
import hashlib
import aiofiles
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
from datetime import datetime

from config.settings import settings

logger = logging.getLogger(__name__)


class FileHandler:
    """Handle file storage, retrieval, and management."""
    
    def __init__(self):
        self.storage_path = Path(settings.cache_dir) / "documents"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Save uploaded file to storage and return file metadata.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            
        Returns:
            Dictionary with file metadata
        """
        try:
            # Generate file hash for deduplication
            file_hash = self._generate_file_hash(file_content)
            
            # Create unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = Path(filename).suffix
            stored_filename = f"{timestamp}_{file_hash[:8]}{file_extension}"
            
            # Full storage path
            storage_file_path = self.storage_path / stored_filename
            
            # Check if file already exists (deduplication)
            if storage_file_path.exists():
                logger.info(f"File already exists: {stored_filename}")
                return await self._get_file_metadata(storage_file_path, filename, file_hash)
            
            # Save file asynchronously
            async with aiofiles.open(storage_file_path, 'wb') as f:
                await f.write(file_content)
            
            logger.info(f"File saved: {filename} -> {stored_filename}")
            
            return await self._get_file_metadata(storage_file_path, filename, file_hash)
            
        except Exception as e:
            logger.error(f"File save failed for {filename}: {e}")
            raise
    
    async def load_file(self, file_id: str) -> Optional[bytes]:
        """
        Load file content by file ID.
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            File content as bytes or None if not found
        """
        try:
            # Find file by ID (stored filename)
            file_path = self.storage_path / file_id
            
            if not file_path.exists():
                logger.warning(f"File not found: {file_id}")
                return None
            
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
            
            logger.info(f"File loaded: {file_id}")
            return content
            
        except Exception as e:
            logger.error(f"File load failed for {file_id}: {e}")
            raise
    
    async def delete_file(self, file_id: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            file_path = self.storage_path / file_id
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {file_id}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_id}")
                return False
                
        except Exception as e:
            logger.error(f"File deletion failed for {file_id}: {e}")
            return False
    
    async def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old files from storage.
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
            
        Returns:
            Number of files deleted
        """
        try:
            deleted_count = 0
            current_time = datetime.now().timestamp()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in self.storage_path.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Cleaned up old file: {file_path.name}")
            
            logger.info(f"Cleanup completed: {deleted_count} files deleted")
            return deleted_count
            
        except Exception as e:
            logger.error(f"File cleanup failed: {e}")
            return 0
    
    def _generate_file_hash(self, file_content: bytes) -> str:
        """Generate SHA-256 hash of file content."""
        return hashlib.sha256(file_content).hexdigest()
    
    async def _get_file_metadata(self, file_path: Path, original_filename: str, file_hash: str) -> Dict[str, Any]:
        """Get file metadata."""
        stat = file_path.stat()
        
        return {
            'file_id': file_path.name,
            'original_filename': original_filename,
            'stored_filename': file_path.name,
            'file_hash': file_hash,
            'file_size': stat.st_size,
            'created_at': datetime.fromtimestamp(stat.st_ctime),
            'modified_at': datetime.fromtimestamp(stat.st_mtime),
            'storage_path': str(file_path)
        }


class TempFileManager:
    """Manage temporary files for processing."""
    
    @staticmethod
    async def create_temp_file(content: bytes, suffix: str = '') -> str:
        """
        Create a temporary file with given content.
        
        Args:
            content: File content
            suffix: File suffix/extension
            
        Returns:
            Path to temporary file
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            logger.debug(f"Temporary file created: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Temporary file creation failed: {e}")
            raise
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> bool:
        """
        Clean up temporary file.
        
        Args:
            file_path: Path to temporary file
            
        Returns:
            True if cleaned up successfully
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug(f"Temporary file cleaned up: {file_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Temporary file cleanup failed: {e}")
            return False
    
    @staticmethod
    async def with_temp_file(content: bytes, suffix: str = ''):
        """
        Context manager for temporary files.
        
        Usage:
            async with TempFileManager.with_temp_file(content, '.pdf') as temp_path:
                # Use temp_path
                pass
        """
        temp_path = None
        try:
            temp_path = await TempFileManager.create_temp_file(content, suffix)
            yield temp_path
        finally:
            if temp_path:
                TempFileManager.cleanup_temp_file(temp_path)