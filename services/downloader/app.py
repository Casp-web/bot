import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from yt_dlp import YoutubeDL

app = FastAPI(title="YouTube Downloader Service")

YOUTUBE_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?(?:m\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=|embed/|v/|.+\?v=)?([\w-]{11})"
)

# yt-dlp options template
YDL_OPTS_COMMON = {
    "restrictfilenames": True,
    "outtmpl": "%\(title\)s.%(ext)s",
    "noplaylist": True,
}

AUDIO_OPTS = {
    **YDL_OPTS_COMMON,
    "format": "bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}

VIDEO_OPTS = {
    **YDL_OPTS_COMMON,
    "format": "best[ext=mp4]/best",
}


class DownloadRequest(BaseModel):
    url: str


def validate_url(url: str) -> None:
    if not YOUTUBE_REGEX.search(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")


@app.post("/download/{media_type}")
async def download(media_type: Literal["audio", "video"], body: DownloadRequest):
    validate_url(body.url)

    tmp_dir = tempfile.mkdtemp()
    target_file: Path | None = None

    ydl_opts = AUDIO_OPTS if media_type == "audio" else VIDEO_OPTS
    ydl_opts["outtmpl"] = os.path.join(tmp_dir, "%\(title\)s.%(ext)s")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(body.url, download=True)
            filename = ydl.prepare_filename(info)
            target_file = Path(filename)
    except Exception as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(exc))

    if not target_file or not target_file.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail="Download failed")

    media_type_header = "audio/mpeg" if media_type == "audio" else "video/mp4"
    background = BackgroundTasks()
    background.add_task(shutil.rmtree, tmp_dir, ignore_errors=True)

    return FileResponse(
        target_file,
        media_type=media_type_header,
        filename=target_file.name,
        background=background,
    )