import keyboard
import math
import cv2 as cv
import numpy as np
import tensorflow as tf
import sys

class Car:
    def __init__(self):
        path = "./cars/basic-black.bmp"
        #self.__position = [210, 260]
        #self.__angle = 0
        #self.__speed = 5
        self.__content = cv.imread(path, cv.IMREAD_UNCHANGED)
        #self.__transformed_content = self.__content
        #self.__direction = [round(math.cos(self.__angle)), round(math.sin(self.__angle))]
        #self.__bounding_box = [
        #    [0,0],
        #    [self.__content.shape[0], self.__content.shape[1]]
        #]
        self.__actions = [
            "up", "down", "right", "left"
            #, "s", "a"
        ]
        self.__brain = self.__create_brain()
        #self.__sensors = [
        #    0, #front
        #    0, #right
        #    0 #left
        #]
        #self.__distance = 0
        #self.__alive = True
        self.reset_state()

    def __create_brain(self):
        output_length = len(self.__actions)

        inputs = tf.keras.Input(shape=(3,))
        x = tf.keras.layers.Dense(3, activation=tf.nn.relu)(inputs)
        outputs = tf.keras.layers.Dense(output_length, activation=tf.nn.softmax)(x)
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        
        return model
    
    def __predict(self, sensors):
        input = np.array([sensors])
        
        output = self.__brain.predict(
            input,
            batch_size=None,
            verbose=0,
            steps=None,
            callbacks=None,
            max_queue_size=10,
            workers=1,
            use_multiprocessing=False,
        )

        max = np.argmax(output[0])
        result = self.__actions[max]

        return result

    def __rotate(self):
        image = self.__content
        angle = self.__angle
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rotation_matrix = cv.getRotationMatrix2D(image_center, angle, 1.0)
        self.__transformed_content = cv.warpAffine(image, rotation_matrix, image.shape[1::-1], flags=cv.INTER_LINEAR)
    
    def __update_rotation(self, action):
        self.__old_angle = self.__angle
        if keyboard.is_pressed("up") or action == "up":
            self.__angle = 90
        
        if keyboard.is_pressed("down") or action == "down":
            self.__angle = -90

        if keyboard.is_pressed("right") or action == "right":
            self.__angle = 0

        if keyboard.is_pressed("left") or action == "left":
            self.__angle = 180
    
    def __update_direction(self):
        angle = (self.__angle * math.pi) / 180
        self.__direction = [int(math.cos(angle)), -1*int(math.sin(angle))]

        old_angle = (self.__old_angle * math.pi) / 180
        old_direction = [int(math.cos(old_angle)), -1*int(math.sin(old_angle))]

        if self.__went_forward_first == None:
            self.__went_forward_first = self.__angle == 0

        if not self.__went_backwards:
            self.__went_backwards = (old_direction == np.dot(-1, self.__direction)).all()

        if self.__forward_only:
            self.__forward_only = old_direction == self.__direction
    
    def __update_speed(self, action):
        if keyboard.is_pressed("s") or action == "s":
            self.__speed = 5
        
        if keyboard.is_pressed("a") or action == "a":
            self.__speed = 0

    def __translate(self, map):
        movement = np.dot(self.__speed, self.__direction)
        position = np.add(self.__position, movement)

        min_bounding_box = np.add(self.__bounding_box[0], movement)
        max_bounding_box = np.add(self.__bounding_box[1], movement)

        bounding_box = [min_bounding_box, max_bounding_box]
        position_available = map.position_available(bounding_box)

        if position_available:
            displacement_vector = np.subtract(position, self.__position)
            self.__distance += math.sqrt(np.dot(displacement_vector, displacement_vector))
            self.__position = position
            self.__bounding_box = bounding_box

        if not position_available:
            self.__alive = False

    def __update_sensors(self, map):
        min_point, max_point = self.__bounding_box
        direction = self.__direction

        center_x = int((max_point[0] - min_point[0])/2) + min_point[0]
        center_y = int((max_point[1] - min_point[1])/2) + min_point[1]

        distances = map.get_distances(direction, (center_x, center_y))

        self.__sensors = distances

    def __randomize_weights(self):
        result = []
        brain = self.__brain
        
        for layer in brain.layers:
            weights = layer.get_weights()

            if len(weights) > 0:
                for weight in weights:
                    #[a, b), b > a -> (b - a) * random_sample() + a
                    a = -sys.maxsize
                    b = sys.maxsize
                    item = (b - a) * np.random.random_sample(weight.shape) + a
                    result.append(item)
        
        return result
    
    def __translate_chromosome(self, chromosome):
        result = []
        brain = self.__brain

        array_start, array_end = 0, 0
        for layer in brain.layers:
            weights = layer.get_weights()

            if len(weights) > 0:
                for weight in weights:
                    size = weight.shape[0]*weight.shape[1] if len(weight.shape) > 1 else weight.shape[0]
                    array_end = array_start + size

                    slice = chromosome[array_start:array_end]
                    item = np.reshape(slice, weight.shape)
                    result.append(item)

                    array_start = array_end

        return result

    def reset_state(self):
        self.__position = [210, 260]
        self.__angle = 0
        self.__old_angle = 0
        self.__went_backwards = False
        self.__went_forward_first = None
        self.__forward_only = True
        self.__speed = 5
        self.__transformed_content = self.__content
        self.__direction = [round(math.cos(self.__angle)), round(math.sin(self.__angle))]
        self.__bounding_box = [
            [self.__position[0], self.__position[1]],
            [self.__content.shape[0] + self.__position[0], self.__content.shape[1] + self.__position[1]]
        ]
        self.__sensors = [
            0, #front
            0, #right
            0 #left
        ]
        self.__distance = 0
        self.__alive = True

    def set_chromosome(self, chromosome=None):
        weights = []
        if chromosome == None:
            weights = self.__randomize_weights()
        else:
            weights = self.__translate_chromosome(chromosome)

        self.__brain.set_weights(weights)

    def get_chromosome(self):
        result = []
        brain = self.__brain

        for layer in brain.layers:
            weights = layer.get_weights()

            if len(weights) > 0:
                for weight in weights:
                    size = weight.shape[0]*weight.shape[1] if len(weight.shape) > 1 else weight.shape[0]
                    item = np.reshape(weight, (1,size))[0].tolist()
                    result += item
        
        return result

    def is_alive(self):
        return self.__alive
    
    def get_distance(self):
        return self.__distance
    
    def went_backwards(self):
        return self.__went_backwards
    
    def went_forward_only(self):
        return self.__forward_only
    
    def went_forward_first(self):
        return self.__went_forward_first

    def transform(self, map):
        self.__update_sensors(map)
        action = self.__predict(self.__sensors)
        self.__update_rotation(action)
        self.__update_direction()
        self.__update_speed(action)

        self.__rotate()
        self.__translate(map)
    
    def render(self):
        return self.__position, self.__transformed_content