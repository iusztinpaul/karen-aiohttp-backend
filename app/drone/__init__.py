from app.drone.controller import DroneController

drone_controller = DroneController('', 8889)


def get_drone_controller():
    return drone_controller
