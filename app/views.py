import asyncio

from aiohttp import web

import logging

from app.drone import get_drone_controller
from app.settings import Commands

logger = logging.getLogger(__name__)


class Connections:
    def __init__(self):
        self._web_sockets = set()

    def register(self, websocket):
        self._web_sockets.add(websocket)
        logger.info('New websocket registered')

    def unregister(self, websocket):
        self._web_sockets.remove(websocket)
        logger.info('New websocket unregistered')


class BaseWebSocketView(web.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connections = Connections()

    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        if not await self.is_valid(self.request, ws):
            await ws.close()
            return ws

        self.connections.register(ws)

        try:
            await self.handler(ws)
        except Exception as e:
            logger.error(e)
        finally:
            self.connections.unregister(ws)
            await ws.close()

            return ws

    async def is_valid(self, request, websocket):
        """
        :param websocket: Do some validation here.
        :return: boolean
        """
        return True

    async def handler(self, websocket):
        """
        :param websocket: Process your websocket here
        """
        pass


class DroneWebSocketView(BaseWebSocketView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dc = get_drone_controller()


class CommandWebSocketView(DroneWebSocketView):
    async def handler(self, websocket):
        while True:
            command = await websocket.receive_str()
            command = command.upper()

            if command == Commands.STOP:
                self.dc.stop()
            elif command == Commands.FORWARD:
                self.dc.forward()
            elif command == Commands.BACKWARDS:
                self.dc.backward()
            elif command == Commands.UP:
                self.dc.up()
            elif command == Commands.DOWN:
                self.dc.down()
            elif command == Commands.LEFT:
                self.dc.left()
            elif command == Commands.RIGHT:
                self.dc.right()
            elif command == Commands.R_CW:
                self.dc.rotate_cw()
            elif command == Commands.R_CCW:
                self.dc.rotate_ccw()
            elif command == Commands.TAKEOFF:
                self.dc.takeoff()
            elif command == Commands.LAND:
                self.dc.land()
            elif command == Commands.F_B:
                self.dc.flip_b()
            elif command == Commands.F_F:
                self.dc.flip_f()
            elif command == Commands.F_L:
                self.dc.flip_l()
            elif command == Commands.F_R:
                self.dc.flip_r()
            elif command == Commands.START_VIDEO:
                self.dc.start_video()
            elif command == Commands.STOP_VIDEO:
                self.dc.stop_video()


class StatusWebSocketView(DroneWebSocketView):
    async def handler(self, websocket):
        while True:
            await websocket.send_json({
                'battery': self.dc.get_battery(),
                'height': self.dc.get_height(),
                'speed': self.dc.get_speed(),
                'flight_time': self.dc.get_flight_time()
            })
            await asyncio.sleep(2)


class HlsVideoView(web.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dc = get_drone_controller()

    async def get(self):
        batch_file_path = self.dc.get_batch_file_path()

        return web.FileResponse(batch_file_path)
