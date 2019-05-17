import socket
import time
import threading

import numpy as np


MAX_TIME_OUT = 15.0


# class VideoReceiver:
#     def __init__(self, cmd_socket, tello_ip, tello_port):
#         self.decoder = libh264decoder.H264Decoder()
#         self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for receiving video stream
#         self.local_video_port = 11111  # port for receiving video stream
#         self.frame = None  # numpy array BGR -- current camera output frame
#
#         self.tello_address = (tello_ip, tello_port)
#
#         self.cmd_socket = cmd_socket
#
#         # thread for receiving cmd ack
#         self.receive_thread = threading.Thread(target=self._receive_video_thread)
#         self.receive_thread.daemon = True
#
#         self.receive_thread.start()
#
#         self.socket_video.bind(('', self.local_video_port))
#
#     def _receive_video_thread(self):
#         """
#         Listens for video streaming (raw h264) from the Tello.
#
#         Runs as a thread, sets self.frame to the most recent frame Tello captured.
#
#         """
#         packet_data = ""
#         while True:
#             print('Loop')
#             try:
#                 res_string, ip = self.socket_video.recvfrom(2048)
#                 packet_data += res_string
#                 # end of frame
#                 if len(res_string) != 1460:
#                     print(packet_data)
#                     for frame in self._h264_decode(packet_data):
#                         self.frame = frame
#                     packet_data = ""
#             except socket.error as exc:
#                 print("Caught exception socket.error : %s" % exc)
#
#     def _h264_decode(self, packet_data):
#         """
#         decode raw h264 format data from Tello
#
#         :param packet_data: raw h264 data array
#
#         :return: a list of decoded frame
#         """
#         res_frame_list = []
#         frames = self.decoder.decode(packet_data)
#         for framedata in frames:
#             (frame, w, h, ls) = framedata
#             if frame is not None:
#                 # print 'frame size %i bytes, w %i, h %i, linesize %i' % (len(frame), w, h, ls)
#
#                 frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
#                 frame = (frame.reshape((h, ls / 3, 3)))
#                 frame = frame[:, :w, :]
#                 res_frame_list.append(frame)
#
#         return res_frame_list
#
#     def send_stream_cmd(self):
#         self.cmd_socket.sendto(b'command', self.tello_address)
#         self.cmd_socket.sendto(b'streamon', self.tello_address)


class CmdController:
    def __init__(self, socket, tello_address, imperial=False, command_timeout=.3):
        self.socket = socket
        self.tello_address = tello_address

        self.response = None
        self.abort_flag = False
        self.command_timeout = command_timeout
        self.imperial = imperial
        self.last_height = 0

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
            response = self.response.decode('utf-8')

        self.response = None

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
        return self.response

    def get_height(self):
        """Returns height(dm) of tello.

        Returns:
            int: Height(dm) of tello.

        """
        height = self.send_command('height?')
        height = str(height)
        height = filter(str.isdigit, height)
        self.last_height = height
        print(f'height: {height}')

        return height

    def get_battery(self):
        """Returns percent battery life remaining.

        Returns:
            int: Percent battery life remaining.

        """

        battery = self.send_command('battery?')
        print(f'battery: {battery}')

        return battery

    def get_flight_time(self):
        """Returns the number of seconds elapsed during flight.

        Returns:
            int: Seconds elapsed during flight.

        """

        flight_time = self.send_command('time?')
        print(f'flight_time: {flight_time}')

        return flight_time

    def get_speed(self):
        """Returns the current speed.

        Returns:
            int: Current speed in KPH or MPH.

        """

        speed = self.send_command('speed?')
        print(f'speed: {speed}')

        return speed

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
            distance = int(round(distance * 100))

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


class DroneController:
    def __init__(self, local_ip='', local_port=8889, tello_ip='192.168.10.1', tello_port=8889):
        self.tello_address = (tello_ip, tello_port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((local_ip, local_port))

        self._cmd_controller = CmdController(self.socket, self.tello_address)

        # self._video_receiver = VideoReceiver(self.cmd_socket, *self.tello_adderss)
        # self._video_receiver.send_stream_cmd()

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

    def get_speed(self):
        self._cmd_controller.get_speed()

    def get_height(self):
        self._cmd_controller.get_height()

    def get_battery(self):
        self._cmd_controller.get_battery()

    def get_flight_time(self):
        self._cmd_controller.get_flight_time()
