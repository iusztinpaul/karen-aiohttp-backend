import logging
import os
import re
import socket
import time
import threading

from multiprocessing.pool import ThreadPool

import ffmpeg

logger = logging.getLogger(__name__)


MAX_TIME_OUT = 15.0


class VideoReceiver:
    VS_UDP_IP = '0.0.0.0'
    VS_UDP_PORT = 11111

    H265_BATCH_SIZE = 100

    def __init__(self, tello_ip, tello_port):
        self.tello_address = (tello_ip, tello_port)
        self.cap = None

        self.grabbed = None
        self.frame = None
        self.stopped = False

        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for receiving video stream
        self.socket_video.bind(('', self.VS_UDP_PORT))

        self.receive_raw_video_thread = threading.Thread(target=self._receive_raw_data_handler)

        self.pipe_h264 = (
            ffmpeg
                .input('pipe:0', format='rawvideo')
                .output('../stream', format='hls', start_number=0, hls_time=1, hls_list_size=0)
        )

    def _receive_raw_data_handler(self):
        """
        Listens for video streaming (raw h264) from the Tello.

        Runs as a thread, sets self.frame to the most recent frame Tello captured.

        """
        packet_data = b''

        while not self.stopped:
            try:
                res_string, ip = self.socket_video.recvfrom(2048)
                packet_data += res_string
                # end of frame
                if len(res_string) != 1460:
                    self.pipe_h264.stdin.write(packet_data)

                    packet_data = b''

            except socket.error as exc:
                print("Caught exception socket.error : {}".format(exc))

        self.stopped = False

    def get_batch_file_path(self):
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self._remove_m3u8_handler, (m3u8_dir_path, ))

        return async_result.get()

    def _remove_m3u8_handler(self, m3u8_dir_path):
        yield m3u8_dir_path

        if os.path.exists(m3u8_dir_path):
            os.remove(m3u8_dir_path)

    def start_video(self):
        self.receive_raw_video_thread.start()
        self.h264_to_m3u8_filter.filter()

    def stop_video(self):
        self.stopped = True
        self.h264_to_m3u8_filter.stop()

        self.pipe_h264.clear()
        self.pipe_m3u8.clear()


class CmdController:
    def __init__(self, socket, tello_address, imperial=False, command_timeout=.3):
        self.socket = socket
        self.tello_address = tello_address

        self.response = None
        self.abort_flag = False
        self.command_timeout = command_timeout
        self.imperial = imperial
        self.last_height = 0

        self.lock = threading.Lock()

        self._command_thread = threading.Thread(target=self._send_command_handler)
        self._command_thread.start()

        self._status_thread = threading.Thread(target=self._get_status_handler)
        self._status_thread.start()

    def send_command(self, command):
        """
        Send a command to the Tello and wait for a response.

        :param command: Command to send.
        :return (str): Response from Tello.

        """

        try:
            self.lock.acquire(True, timeout=0.05)

            print(">> send cmd: {}".format(command))
            self.abort_flag = False
            timer = threading.Timer(self.command_timeout, self.set_abort_flag)

            self.socket.sendto(command.encode('utf-8'), self.tello_address)

            timer.start()
            while self.response is None:
                if self.abort_flag is True:
                    break
            timer.cancel()

            if self.response is None:
                response = 'none_response'
            else:
                try:
                    response = self.response.decode('utf-8')
                except UnicodeDecodeError as e:
                    print(f'UnicodeDecodeError: {e}')
                    response = 'none_response'

            self.response = None
        finally:
            self.lock.release()

        return response

    def set_abort_flag(self):
        """
        Sets self.abort_flag to True.

        Used by the timer in Tello.send_command() to indicate to that a response

        timeout has occurred.

        """

        self.abort_flag = True

    def _send_command_handler(self):
        """
        start a while loop that sends 'command' to tello every 5 second
        """
        while True:
            self.send_command('command')
            time.sleep(30)

    def _get_status_handler(self):
        """Listen to responses from the Tello.

        Runs as a thread, sets self.response to whatever the Tello last returned.

        """
        while True:
            try:
                self.response, ip = self.socket.recvfrom(3000)
            except socket.error as exc:
                print("Caught exception socket.error : %s".format(exc))

    @property
    def get_status(self):
        return self.response

    def takeoff(self):
        """
        Initiates take-off.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        result = self.send_command('takeoff')
        print(f'Takeoff: {result}')
        return result

    def set_speed(self, speed):
        """
        Sets speed.

        This method expects KPH or MPH. The Tello API expects speeds from
        1 to 100 centimeters/second.

        Metric: .1 to 3.6 KPH
        Imperial: .1 to 2.2 MPH

        Args:
            speed (int|float): Speed.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        speed = float(speed)

        if self.imperial is True:
            speed = int(round(speed * 44.704))
        else:
            speed = int(round(speed * 27.7778))

        return self.send_command('speed %s' % speed)

    def rotate_cw(self, degrees):
        """
        Rotates clockwise.

        Args:
            degrees (int): Degrees to rotate, 1 to 360.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        result = self.send_command('cw %s' % degrees)
        print(f'rotate_cw: {result}')

        return result

    def rotate_ccw(self, degrees):
        """
        Rotates counter-clockwise.

        Args:
            degrees (int): Degrees to rotate, 1 to 360.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """
        result = self.send_command('ccw %s' % degrees)
        print(f'rotate_ccw: {result}')

        return result

    def flip(self, direction):
        """
        Flips.

        Args:
            direction (str): Direction to flip, 'l', 'r', 'f', 'b'.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.send_command('flip %s' % direction)

    def get_response(self):
        """
        Returns response of tello.

        Returns:
            int: response of tello.

        """
        response = self.response
        return response

    def get_height(self):
        """Returns height(dm) of tello.

        Returns:
            str: Height(dm) of tello.

        """
        height = self.send_command('height?')

        try:
            height = str(height)
            self.last_height = height
        except:
            height = self.last_height
            pass

        return height

    def get_battery(self):
        """Returns percent battery life remaining.

        Returns:
            str: Percent battery life remaining.

        """

        battery = self.send_command('battery?')

        return str(battery)

    def get_flight_time(self):
        """Returns the number of seconds elapsed during flight.

        Returns:
            str: Seconds elapsed during flight.

        """

        flight_time = self.send_command('time?')

        return str(flight_time)

    def get_speed(self):
        """Returns the current speed.

        Returns:
            str: Current speed in KPH or MPH.

        """

        speed = self.send_command('speed?')

        return str(speed)

    def land(self):
        """Initiates landing.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        result = self.send_command('land')
        print(f'Land: {result}')
        return result

    def move(self, direction, distance):
        """Moves in a direction for a distance.

        This method expects meters or feet. The Tello API expects distances
        from 20 to 500 centimeters.

        Metric: .02 to 5 meters
        Imperial: .7 to 16.4 feet

        Args:
            direction (str): Direction to move, 'forward', 'back', 'right' or 'left'.
            distance (int|float): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        distance = float(distance)

        if self.imperial is True:
            distance = int(round(distance * 30.48))
        else:
            distance = int(round(distance * 30))

        result = self.send_command('%s %s' % (direction, distance))
        print(f'move: {result}')

        return result

    def move_backward(self, distance):
        """Moves backward for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.move('back', distance)

    def move_down(self, distance):
        """Moves down for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.move('down', distance)

    def move_forward(self, distance):
        """Moves forward for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """
        return self.move('forward', distance)

    def move_left(self, distance):
        """Moves left for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """
        return self.move('left', distance)

    def move_right(self, distance):
        """Moves right for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        """
        return self.move('right', distance)

    def move_up(self, distance):
        """Moves up for a distance.

        See comments for Tello.move().

        Args:
            distance (int): Distance to move.

        Returns:
            str: Response from Tello, 'OK' or 'FALSE'.

        """

        return self.move('up', distance)

    def stop(self):
        return self.send_command('stop')

    def start_video(self):
        self.send_command('command')
        return self.send_command('streamon')

    def stop_video(self):
        self.send_command('command')
        return self.send_command('streamoff')


class DroneController:
    def __init__(self, local_ip='', local_port=8889, tello_ip='192.168.10.1', tello_port=8889):
        self.tello_address = (tello_ip, tello_port)
        self.socket = self._create_socket(local_ip, local_port)

        self._cmd_controller = CmdController(self.socket, self.tello_address)

        self._video_receiver = VideoReceiver(*self.tello_address)

    def _create_socket(self, local_ip, local_port):
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.bind((local_ip, local_port))
                return s
            except OSError as e:
                print(f'Error on creating socket. Retrying in 0.5s : {e}')
                time.sleep(0.5)

    def land(self):
        self._cmd_controller.land()

    def takeoff(self):
        self._cmd_controller.takeoff()

    def forward(self):
        self._cmd_controller.move_forward(1)

    def backward(self):
        self._cmd_controller.move_backward(1)

    def right(self):
        self._cmd_controller.move_right(1)

    def left(self):
        self._cmd_controller.move_left(1)

    def up(self):
        self._cmd_controller.move_up(1)

    def down(self):
        self._cmd_controller.move_down(1)

    def rotate_cw(self):
        self._cmd_controller.rotate_cw(15)

    def rotate_ccw(self):
        self._cmd_controller.rotate_ccw(15)

    def flip_f(self):
        self._cmd_controller.flip('f')

    def flip_b(self):
        self._cmd_controller.flip('b')

    def flip_l(self):
        self._cmd_controller.flip('l')

    def flip_r(self):
        self._cmd_controller.flip('r')

    def stop(self):
        self._cmd_controller.stop()

    def get_speed(self):
        speed = self._cmd_controller.get_speed()
        return self._correct_data(speed)

    def get_height(self):
        height = self._cmd_controller.get_height()
        return self._correct_data(height)

    def get_battery(self):
        battery = self._cmd_controller.get_battery()
        return self._correct_data(battery)

    def get_flight_time(self):
        flight_time = self._cmd_controller.get_flight_time()
        return self._correct_data(flight_time)

    def _correct_data(self, data: str):
        if data:
            match = re.search(r'(?P<number_data>[0-9]*)', data)
            data = match and match.group('number_data')

            if data:
                return data

        return None

    def start_video(self):
        self._video_receiver.start_video()
        return self._cmd_controller.start_video()

    def stop_video(self):
        return self._cmd_controller.stop_video()

    def get_batch_file_path(self):
        return self._video_receiver.get_batch_file_path()
