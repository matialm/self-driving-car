import cv2 as cv
import numpy as np

class Device:
    def __init__(self, size):
        self.__fps = 60
        self.__name = "self-driving car"
        self.__size = size
        self.__screen = np.zeros([self.__size[0], self.__size[1], 3])
    
    def __generate_frame(self, models):
        self.__clean()
        frame = self.__screen
        
        for model in models:
            position, content = model.render()

            x_offset, y_offset = position
            height, width, _ = content.shape

            frame[y_offset:y_offset+height, x_offset:x_offset+width] = content
        
        return frame
    
    def __clean(self):
        self.__screen = np.zeros([self.__size[0], self.__size[1], 3])
    
    def render(self, models):
        frame = self.__generate_frame(models)
        cv.imshow(self.__name, frame)
        cv.waitKey(int(1000/self.__fps))
    
    def stop(self):
        cv.destroyAllWindows()