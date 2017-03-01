"""Image color space conversions."""

import numpy as np


def rgb2rdgdb(image):
    r = image[:,:,0]
    g = image[:,:,1]
    b = image[:,:,2]

    new_image = np.empty_like(image)

    new_image[:,:,0] = r
    new_image[:,:,1] = np.mod(r - g + 128, 256)
    new_image[:,:,2] = np.mod(g - b + 128, 256)

    return new_image


def rdgdb2rgb(image):
    r = image[:,:,0]
    dg = image[:,:,1]
    db = image[:,:,2]

    new_image = np.empty_like(image)

    g = np.mod(r - dg + 128, 256)
    b = np.mod(g - db + 128, 256)
    new_image[:,:,0] = r
    new_image[:,:,1] = g
    new_image[:,:,2] = b

    return new_image
