import ffmpeg

from app.pipes_and_filters.pipes_and_filters.pipes import Pipe
from app.pipes_and_filters.common.handlers import Handler


# class H284ToM3U8Handler(Handler):
#     CURRENT_FILE_INDEX = 0
#     MAX_FILE_INDEX = Pipe.QUEUE_MAX_SIZE
#     FILE_PREFIX = 'm3u8'
#
#     @classmethod
#     def handle(cls, data):
#         # process all the mp4 from the pipe and compute a m3u8
#         subprocess = (
#             ffmpeg
#                 .input('pipe:')
#                 .output(output_file, format='hls', start_number=0, hls_time=1, hls_list_size=0)
#                 .overwrite_output()
#                 .run_async(pipe_stdin=True)
#         )
#
#         file_path = '/Users/pauliusztin/Desktop/karen-aiohttp-backend/data'
#
#         return file_path
#
#     @classmethod
#     def get_file_name(cls):
#         return f'{cls.FILE_PREFIX}_{cls.CURRENT_FILE_INDEX}.m3u8'
#
#     @classmethod
#     def next_file(cls):
#         if cls.CURRENT_FILE_INDEX < cls.MAX_FILE_INDEX:
#             cls.CURRENT_FILE_INDEX = cls.CURRENT_FILE_INDEX + 1
#         else:
#             cls.CURRENT_FILE_INDEX = 0


