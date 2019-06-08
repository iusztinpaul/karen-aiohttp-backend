from aiohttp import web
from app import create
from app.image_recognition.image_process import StreamToImagesThread, ImageProcessingThread

stream_to_image_thread = StreamToImagesThread()
stream_to_image_thread.start()

image_process_thread = ImageProcessingThread()
image_process_thread.start()

app = create()
web.run_app(app)
