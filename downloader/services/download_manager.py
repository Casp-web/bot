import asyncio
import os
from typing import Dict, Optional, Callable, Any
from datetime import datetime
from pathlib import Path

from loguru import logger
from downloader.services.youtube_service import YouTubeService
from downloader.models.video_info import VideoInfo
from config.settings.base import settings


class DownloadTask:
    """Represents a single download task"""
    
    def __init__(self, task_id: str, user_id: int, video_info: VideoInfo, 
                 download_type: str, quality: str = None):
        self.task_id = task_id
        self.user_id = user_id
        self.video_info = video_info
        self.download_type = download_type  # 'video' or 'audio'
        self.quality = quality
        self.status = "pending"  # pending, downloading, completed, failed
        self.progress = 0
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.file_path: Optional[str] = None
        self.error_message: Optional[str] = None
        self.progress_callback: Optional[Callable] = None


class DownloadManager:
    """Manages download queue and concurrent downloads"""
    
    def __init__(self):
        self.youtube_service = YouTubeService()
        self.active_downloads: Dict[str, DownloadTask] = {}
        self.download_queue: asyncio.Queue = asyncio.Queue()
        self.max_concurrent_downloads = settings.MAX_CONCURRENT_DOWNLOADS
        self.worker_tasks: list = []
        self._running = False
    
    async def start(self):
        """Start the download manager workers"""
        if self._running:
            return
        
        self._running = True
        logger.info(f"Starting download manager with {self.max_concurrent_downloads} workers")
        
        # Start worker tasks
        for i in range(self.max_concurrent_downloads):
            task = asyncio.create_task(self._download_worker(f"worker-{i}"))
            self.worker_tasks.append(task)
    
    async def stop(self):
        """Stop the download manager workers"""
        if not self._running:
            return
        
        self._running = False
        logger.info("Stopping download manager")
        
        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to finish
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()
    
    async def add_download(self, task_id: str, user_id: int, video_info: VideoInfo,
                          download_type: str, quality: str = None,
                          progress_callback: Callable = None) -> DownloadTask:
        """Add a new download task to the queue"""
        
        # Check if task already exists
        if task_id in self.active_downloads:
            return self.active_downloads[task_id]
        
        # Create download task
        task = DownloadTask(task_id, user_id, video_info, download_type, quality)
        task.progress_callback = progress_callback
        
        # Add to active downloads
        self.active_downloads[task_id] = task
        
        # Add to queue
        await self.download_queue.put(task)
        
        logger.info(f"Added download task {task_id} for user {user_id}")
        return task
    
    async def get_download_status(self, task_id: str) -> Optional[DownloadTask]:
        """Get the status of a download task"""
        return self.active_downloads.get(task_id)
    
    async def cancel_download(self, task_id: str) -> bool:
        """Cancel a download task"""
        task = self.active_downloads.get(task_id)
        if not task:
            return False
        
        if task.status == "downloading":
            # TODO: Implement actual cancellation of download process
            task.status = "cancelled"
            task.error_message = "Download cancelled by user"
        elif task.status == "pending":
            task.status = "cancelled"
            task.error_message = "Download cancelled by user"
        
        logger.info(f"Cancelled download task {task_id}")
        return True
    
    async def _download_worker(self, worker_name: str):
        """Worker coroutine that processes download tasks"""
        logger.info(f"Download worker {worker_name} started")
        
        while self._running:
            try:
                # Get task from queue with timeout
                task = await asyncio.wait_for(
                    self.download_queue.get(), 
                    timeout=1.0
                )
                
                logger.info(f"Worker {worker_name} processing task {task.task_id}")
                await self._process_download_task(task)
                
            except asyncio.TimeoutError:
                # No tasks in queue, continue waiting
                continue
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_name} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                continue
        
        logger.info(f"Download worker {worker_name} stopped")
    
    async def _process_download_task(self, task: DownloadTask):
        """Process a single download task"""
        try:
            task.status = "downloading"
            task.started_at = datetime.now()
            
            # Create progress callback
            async def progress_callback(progress_info: dict):
                task.progress = progress_info.get('percentage', 0)
                if task.progress_callback:
                    await task.progress_callback(task, progress_info)
            
            # Perform the actual download
            if task.download_type == "video":
                file_path = await self.youtube_service.download_video(
                    task.video_info.url,
                    output_path=settings.DOWNLOAD_PATH,
                    quality=task.quality,
                    progress_callback=progress_callback
                )
            elif task.download_type == "audio":
                file_path = await self.youtube_service.download_audio(
                    task.video_info.url,
                    output_path=settings.DOWNLOAD_PATH,
                    quality=task.quality,
                    progress_callback=progress_callback
                )
            else:
                raise ValueError(f"Unknown download type: {task.download_type}")
            
            # Update task status
            task.status = "completed"
            task.completed_at = datetime.now()
            task.file_path = file_path
            task.progress = 100
            
            logger.info(f"Download task {task.task_id} completed: {file_path}")
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()
            
            logger.error(f"Download task {task.task_id} failed: {e}")
        
        finally:
            # Notify completion
            if task.progress_callback:
                try:
                    await task.progress_callback(task, {"status": task.status})
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")
    
    async def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up completed tasks older than max_age_hours"""
        now = datetime.now()
        to_remove = []
        
        for task_id, task in self.active_downloads.items():
            if task.status in ["completed", "failed", "cancelled"]:
                if task.completed_at:
                    age_hours = (now - task.completed_at).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.active_downloads[task_id]
            logger.info(f"Cleaned up old task {task_id}")
        
        return len(to_remove)
    
    def get_user_active_downloads(self, user_id: int) -> list[DownloadTask]:
        """Get all active downloads for a specific user"""
        return [
            task for task in self.active_downloads.values()
            if task.user_id == user_id and task.status in ["pending", "downloading"]
        ]
    
    def get_download_statistics(self) -> dict:
        """Get download statistics"""
        stats = {
            "total_tasks": len(self.active_downloads),
            "pending": 0,
            "downloading": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }
        
        for task in self.active_downloads.values():
            stats[task.status] = stats.get(task.status, 0) + 1
        
        return stats


# Global download manager instance
download_manager = DownloadManager()