from map import Map
from car import Car
from device import Device
from evolution import Evolution
import keyboard

class Engine:
    def __init__(self):
        screen_size = (300, 500)
        self.__device = Device(screen_size)
    
    def start(self):
        map = Map([0, 0])
        evolution = Evolution()
        evolution.create_initial_population()

        stop = False
        epoch = 0
        max_epoch = 100
        while not stop:
            if keyboard.is_pressed("escape"):
                stop = True

            cars = evolution.get_population()

            for car in cars:
                if car.is_alive():
                    car.transform(map)

            models = [map] + cars
            self.__device.render(models)

            everyone_is_dead = all([not car.is_alive() for car in cars])
            
            if everyone_is_dead or epoch > max_epoch:
                epoch = 0
                evolution.create_next_generation()
            
            epoch += 1