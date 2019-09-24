__author__ = 'AlexH'
    # the types used to store the sky areas
#    SkyArea = namedtuple("SkyArea", ["id", "image_files", "field_rect", "sigma_rect"])
#    ImageFile = namedtuple("ImageFile", ["id", "wavelength", "sigma", "file_name"])
#    SigmaRect = namedtuple("SigmaRect", ["bottom", "top", "left", "right"])
#    FieldRect = namedtuple("FieldRect",["bottom", "top", "left", "right"])

class SkyArea(object):

    def __init__(self, id, image_files=None, field_rect=None, sigma_rect=None):
        self.id = id
        self.image_files = image_files
        if self.image_files == None:
            self.image_files = {}
        self.field_rect = field_rect
        self.sigma_rect = sigma_rect


class ImageFile(object):

    def __init__(self, id, wavelength, file_name, sigma=None, threshold=None):
        self.id = id
        self.wavelength = wavelength
        self.file_name = file_name
        self.sigma = sigma
        self.threshold = threshold

class FieldRect(object):

    def __init__(self, bottom, top, left, right):
        self.bottom = bottom
        self.top = top
        self.left = left
        self.right = right


class SigmaRect(object):

    def __init__(self, bottom, top, left, right):
        self.bottom = bottom
        self.top = top
        self.left = left
        self.right = right

