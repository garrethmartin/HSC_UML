__author__ = 'ah14aeb'

import random

class BoundingBox(object):

    #left = 0
    #right = 0
    #top = 0
    #bottom = 0
    #width = 0
    #height = 0
    #xpixel_range = None
    #ypixel_range = None

    def __init__(self, left, right, top, bottom, step=1):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.width = right - left
        self.height = top - bottom
        self.x_pixel_range = range(left, right, step)
        self.y_pixel_range = range(bottom, top, step)

    def in_box(self, x, y):
        if x < self.left or x > self.right or y > self.top or y < self.bottom:
            return False
        else:
            return True

    def get_random_position(self):
        x = random.choice(self.x_pixel_range)
        y = random.choice(self.y_pixel_range)
        return x, y

    def print_details(self):
        return "top: {0} left: {1}, bottom: {2} right: {3}".format(self.top, self.left, self.bottom, self.right)
