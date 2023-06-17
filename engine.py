from device import Device
from map import Map
from car import Car
import keyboard

class Engine:
    def __init__(self):
        screen_size = (300, 500)
        self.__device = Device(screen_size)
    
    def start(self):
        start_point = [210, 260]
        map = Map([0, 0])
        models = []
        models.append(map)
        models.append(Car(start_point, map))

        stop = False
        while not stop:
            if keyboard.is_pressed("escape"):
                stop = True
            
            for model in models:
                model.transform()

            self.__device.render(models)