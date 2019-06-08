import asyncio
import logging
import os
import subprocess as sp
import time
from threading import Thread
from aiohttp_requests import requests
import app.image_recognition.recognition as recognition

logger = logging.getLogger(__name__)


class StreamToImagesThread(Thread):
    INDIR = f'{os.getcwd()}/app/stream'
    INFILE = f'{INDIR}/data' #stream.m3u8'
    OUTFILE = "app/photos/"

    def __init__(self):
        super().__init__()
        self.stopped = False

    def run(self):
        self.stopped = False
        # ffmpeg -i filename.m3u8  -f image2 -vf fps=fps=1 img%03d.jpg

        # stream = (
        #             ffmpeg
        #                 .input(self.INFILE)
        #                 .filter('fps', fps=25, round='up')
        #                 .output(self.OUTFILE, format='image2')
        #                 .compile()
        #             )


        # command = ['ffmpeg',
        #            '-y',  # (optional) overwrite output file if it exists
        #            '-f', 'rawvideo',
        #            '-vcodec', 'rawvideo',
        #            '-s', '420x360',  # size of one frame
        #            '-pix_fmt', 'rgb24',
        #            '-r', '24',  # frames per second
        #            '-i', f'{os.getcwd()}/{self.INFILE}',  # The imput comes from a pipe
        #            '-an',  # Tells FFMPEG not to expect any audio
        #            '-vcodec', f'{os.getcwd()}/my_output_videofile.mp4']

        command = ['ffmpeg',
                   '-i',  f'{self.INFILE}',
                   '-r', '1',
                   f'{self.OUTFILE}/output_%03d.png']

        while not self.stopped:

            while len(os.listdir(f'{self.INDIR}')) == 0:
                continue

            sp.Popen(command)
            time.sleep(30)

        self.stopped = False

    def stop(self):
        self.stopped = True


class ImageProcessingThread(Thread):
    INDIR = f'{os.getcwd()}/app/photos'

    def __init__(self):
        super().__init__()
        self.manager = recognition.AIManager()

    def run(self):
        # loop = asyncio.get_event_loop()

        for objects, base64obj in recognition.get_results_from_photos(self.INDIR, self.manager):
            print(objects)
            # if objects:
                # loop.run_until_complete(self._make_request(base64obj))

    async def _make_request(self, base64obj):
        payload = {
            "droneId": "Keren-001",
            "image": base64obj
        }
        response = await requests.post('http://192.168.6.100:8080/event', data=payload)
        response_json = await response.json()

        logger.info(f'Photo response: {response_json}')


