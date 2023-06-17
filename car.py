import cv2 as cv
import numpy as np
import keyboard
import math

class Car:
    def __init__(self, position, map):
        path = "./cars/basic-black.bmp"
        self.__position = position
        self.__angle = 0
        self.__speed = 0
        self.__content = cv.imread(path, cv.IMREAD_UNCHANGED)
        self.__transformed_content = self.__content
        self.direction = [round(math.cos(self.__angle)), round(math.sin(self.__angle))]
        self.__map = map
        self.alive = True
        self.distance = 0
        self.sensors = [
            0, #front
            0, #left
            0 #right
        ]
        self.__bounding_box = [
            [0,0],
            [self.__content.shape[0], self.__content.shape[1]]
        ]

    def __rotate(self):
        image = self.__content
        angle = self.__angle
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rotation_matrix = cv.getRotationMatrix2D(image_center, angle, 1.0)
        self.__transformed_content = cv.warpAffine(image, rotation_matrix, image.shape[1::-1], flags=cv.INTER_LINEAR)
    
    def __update_rotation(self):
        if keyboard.is_pressed("up"):
            self.__angle = 90
        
        if keyboard.is_pressed("down"):
            self.__angle = -90

        if keyboard.is_pressed("right"):
            self.__angle = 0

        if keyboard.is_pressed("left"):
            self.__angle = 180
    
    def __update_direction(self):
        angle = (self.__angle * math.pi) / 180
        self.__direction = [int(math.cos(angle)), -1*int(math.sin(angle))]
    
    def __update_speed(self):
        if keyboard.is_pressed("s"):
            self.__speed += 1
        
        if keyboard.is_pressed("a"):
            self.__speed = 0
    
    def __translate(self):
        new_position = self.__position.copy()
        new_min_bounding_box_point = self.__bounding_box[0].copy()
        new_max_bounding_box_point = self.__bounding_box[1].copy()

        new_position[0] += self.__speed * self.__direction[0]
        new_position[1] += self.__speed * self.__direction[1]

        new_min_bounding_box_point[0] += new_position[0]
        new_min_bounding_box_point[1] += new_position[1]

        new_max_bounding_box_point[0] += new_position[0]
        new_max_bounding_box_point[1] += new_position[1]

        new_bounding_box = [new_min_bounding_box_point, new_max_bounding_box_point]
        position_available = self.__map.position_available(new_bounding_box)

        if self.__position != new_position and position_available:
            self.distance += abs(new_position[0] - self.__position[0]) + abs(new_position[1] - self.__position[1])
            self.__position = new_position

        if not position_available:
            self.alive = False
    
    def transform(self):
        self.__update_rotation()
        self.__update_direction()
        self.__update_speed()

        self.__translate()
        self.__rotate()
    
    def render(self):
        return self.__position, self.__transformed_content