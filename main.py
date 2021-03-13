from uuid import getnode as get_mac
import requests
import os
from urllib.request import urlopen
from tqdm import tqdm
from fastapi import FastAPI, BackgroundTasks
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, HttpUrl
import subprocess

app = FastAPI()


class Video(BaseModel):
    name: str


class VideoDownload(BaseModel):
    url: HttpUrl
    name: str
    mimetype: str


@app.on_event("startup")
def setup_env():
    if not os.path.exists('videos'):
        os.mkdir('videos')


@app.post('/api/present')
async def handle_present_video(data: Video):
    if not data.name:
        raise HTTPException(
            status_code=400,
            detail="Video name is required field"
        )

    # Do something with present video

    return {
        "status": "OK"
    }


@app.post('/api/download-video')
async def handle_download_video_by_url(video: VideoDownload, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        download_from_url, video.url, f"videos/{video.name}.{video.mimetype}"
    )

    return {
        "status": "OK",
        "message": "Download video task sent in the background"
    }


@app.get('/api/videos')
async def handle_get_videos():
    return {
        "status": "OK",
        "data": {
            "videos": os.listdir('videos')
        }
    }


@app.get('/api/mac-address')
async def handle_get_mac_address():
    mac = get_mac()
    h = iter(hex(mac)[2:].zfill(12))
    mac_address = ":".join(i + next(h) for i in h)
    return {
        "status": "OK",
        "data": {
            'mac_address': mac_address.upper()
        },
        "message": None
    }


@app.delete('/api/delete-video')
async def handle_delete_video(data: Video):
    filepath = f"videos/{data.name}"
    if not os.path.exists(filepath):
        raise HTTPException(
            400,
            detail=f"Video {data.name} does not exist"
        )

    os.remove(filepath)
    return {
        "status": "OK",
        "message": f"Video {data.name} is deleted"
    }


def download_from_url(url, dst):
    """
    @param: url to download file
    @param: dst place to put the file
    """
    file_size = int(urlopen(url).info().get('Content-Length', -1))
    if os.path.exists(dst):
        first_byte = os.path.getsize(dst)
    else:
        first_byte = 0
    if first_byte >= file_size:
        return file_size
    header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
    process_bar = tqdm(
        total=file_size, initial=first_byte,
        unit='B', unit_scale=True, desc=url.split('/')[-1])
    req = requests.get(url, headers=header, stream=True)
    with open(dst, 'ab') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                process_bar.update(1024)
    process_bar.close()
    return file_size
