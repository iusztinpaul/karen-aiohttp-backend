# Karen the Drone
## Garbage Object Detector with Deep Learning

Microservice that communicates with a Tellur Drone. By an API built in `aiohttp` you can:
  * send control commands to the drone
  * get status from the drone
  * download the video stream from the drone

On the video frames a object detector is ran to detect garbage items.
The role of this microservice is to be hooked to a GUI & to see where there are garbage clusters in places hard accesible.
