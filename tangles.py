'''transpose/angles: enables rotation > 60 degrees by transposing if necessary'''
from PIL import Image

def transpose_angle(angle):
    transpose = None
    if angle > 60:
        transpose = Image.Transpose.ROTATE_90
        angle -= 90
    elif angle < -60:
        transpose = Image.Transpose.ROTATE_270
        angle += 90
    return transpose,angle

def trotate(img,angle):
    '''rotate, but use tranpose to permit angles larger than 60 degrees'''
    transpose,angle = transpose_angle(angle)
    if transpose:
        img = img.transpose(method=transpose)
    if angle:
        img = img.rotate(angle,expand=True)
    return img

def trotate_back(img,angle):
    '''undo rotation done by trotate'''
    transpose,angle = transpose_angle(-angle)
    if angle:
        img = img.rotate(angle,expand=False)
    if transpose:
        img = img.transpose(method=transpose)
    return img

