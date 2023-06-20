import cv2 as cv
import numpy as np

class Map:
    def __init__(self, position):
        path = "./maps/easy.bmp"
        self.__position = position
        self.__content = cv.imread(path, cv.IMREAD_UNCHANGED)
        external_bounding_box, internal_bounding_box = self.__create_bounding_box()

        self.__external_bounding_box = external_bounding_box
        self.__internal_bounding_box = internal_bounding_box
    
    def __create_bounding_box(self):
        imgray = cv.cvtColor(self.__content, cv.COLOR_BGR2GRAY)
        _, thresh = cv.threshold(imgray, 254, 255, cv.THRESH_BINARY)
        countours, _ = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

        #internal box
        min_internal_point = max_internal_point = None
        for c in countours[1]:
            point = [c[0][0], c[0][1]]

            if min_internal_point == None or point < min_internal_point:
                min_internal_point = point
            
            if max_internal_point == None or point > max_internal_point:
                max_internal_point = point

        #external box
        min_external_point = max_external_point = None
        for c in countours[2]:
            point = [c[0][0], c[0][1]]

            if min_external_point == None or point < min_external_point:
                min_external_point = point
            
            if max_external_point == None or point > max_external_point:
                max_external_point = point
        
        return [min_external_point, max_external_point], [min_internal_point, max_internal_point]
    
    def position_available(self, item_bounding_box):
        external_min_point, external_max_point = self.__external_bounding_box
        internal_min_point, internal_max_point = self.__internal_bounding_box
        item_min_point, item_max_point = item_bounding_box

        outside_internal_box_low = item_min_point[1] > internal_max_point[1]
        outside_internal_box_top = item_max_point[1] < internal_min_point[1]
        outside_internal_box_right = item_min_point[0] > internal_max_point[0]
        outside_internal_box_left = item_max_point[0] < internal_min_point[0]

        outside_internal_box = outside_internal_box_low or outside_internal_box_top or outside_internal_box_right or outside_internal_box_left

        inside_external_box_low = item_max_point[1] < external_max_point[1]
        inside_external_box_top = item_min_point[1] > external_min_point[1]
        inside_external_box_right = item_max_point[0] < external_max_point[0]
        inside_external_box_left = item_min_point[0] > external_min_point[0]

        inside_external_box = inside_external_box_low and inside_external_box_top and inside_external_box_right and inside_external_box_left

        inside_map = outside_internal_box and inside_external_box

        return inside_map

    def __get_front_distance(self, direction, center):
        external_min_point, external_max_point = self.__external_bounding_box
        internal_min_point, internal_max_point = self.__internal_bounding_box
        x, y = center
        distance = 0

        if direction[0] == 1:
            if x > external_min_point[0] and x < internal_min_point[0] and y > internal_min_point[1] and y < internal_max_point[1]:
                #a la izquierda de la caja interna
                distance = internal_min_point[0] - x
            else:
                distance = external_max_point[0] - x

        if direction[0] == -1:
            if x > internal_max_point[0] and x < external_max_point[0] and y > internal_min_point[1] and y < internal_max_point[1]:
                #a la derecha de la caja interna
                distance = x - internal_max_point[0]
            else:
                distance = x - external_min_point[0]
        
        if direction[1] == 1:
            if x > internal_min_point[0] and x < internal_max_point[0] and y > external_min_point[1] and y < internal_min_point[1]:
                #sobre de la caja interna
                distance = internal_min_point[1] - y
            else:
                distance = external_max_point[1] - y

        if direction[1] == -1:
            if x > internal_min_point[0] and x < internal_max_point[0] and y > internal_max_point[1] and y < external_max_point[1]:
                #bajo de la caja interna
                distance = y - internal_max_point[1]
            else:
                distance = y - external_min_point[1]

        return distance
    
    def __right_distance(self, direction, center):
        external_min_point, external_max_point = self.__external_bounding_box
        internal_min_point, internal_max_point = self.__internal_bounding_box
        x, y = center
        distance = 0

        if direction[0] == 1:
            if x > internal_min_point[0] and x < internal_max_point[0] and y > external_min_point[1] and y < internal_min_point[1]:
                #sobre de la caja interna
                distance = internal_min_point[1] - y
            else:
                distance = external_max_point[1] - y

        if direction[0] == -1:
            if x > internal_min_point[0] and x < internal_max_point[0] and y > internal_max_point[1] and y < external_max_point[1]:
                #bajo de la caja interna
                distance = y - internal_max_point[1]
            else:
                distance = y - external_min_point[1]

        if direction[1] == 1:
            if x > internal_max_point[0] and x < external_max_point[0] and y > internal_min_point[1] and y < internal_max_point[1]:
                #a la derecha de la caja interna
                distance = x - internal_max_point[0]
            else:
                distance = x - external_min_point[0]
        
        if direction[1] == -1:
            if x > external_min_point[0] and x < internal_min_point[0] and y > internal_min_point[1] and y < internal_max_point[1]:
                #a la izquierda de la caja interna
                distance = internal_min_point[0] - x
            else:
                distance = external_max_point[0] - x

        return distance
    
    def __left_distance(self, direction, center):
        external_min_point, external_max_point = self.__external_bounding_box
        internal_min_point, internal_max_point = self.__internal_bounding_box
        x, y = center
        distance = 0

        if direction[0] == 1:
            if x > internal_min_point[0] and x < internal_max_point[0] and y > internal_max_point[1] and y < external_max_point[1]:
                #bajo de la caja interna
                distance = y - internal_max_point[1]
            else:
                distance = y - external_min_point[1]

        if direction[0] == -1:
            if x > internal_min_point[0] and x < internal_max_point[0] and y > external_min_point[1] and y < internal_min_point[1]:
                #sobre de la caja interna
                distance = internal_min_point[1] - y
            else:
                distance = external_max_point[1] - y

        if direction[1] == 1:
            if x > external_min_point[0] and x < internal_min_point[0] and y > internal_min_point[1] and y < internal_max_point[1]:
                #a la izquierda de la caja interna
                distance = internal_min_point[0] - x
            else:
                distance = external_max_point[0] - x

        if direction[1] == -1:
            if x > internal_max_point[0] and x < external_max_point[0] and y > internal_min_point[1] and y < internal_max_point[1]:
                #a la derecha de la caja interna
                distance = x - internal_max_point[0]
            else:
                distance = x - external_min_point[0]

        return distance

    def get_distances(self, direction, center):
        front_distance = self.__get_front_distance(direction, center)
        right_distance = self.__right_distance(direction, center)
        left_distance = self.__left_distance(direction, center)

        return [front_distance, right_distance, left_distance]
    
    def transform(self):
        pass

    def render(self):
        return self.__position, self.__content