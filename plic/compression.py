"""The compression algorithm."""

from math import ceil
import numpy as np
from scipy import misc

import pickle
import pickletools
import zlib


def downsample(image, t):
    """Downsample an image by skipping `t` pixels."""
    return np.copy(image[::t,::t,:])


def interpolate(image, shape):
    """Up-size an image by a factor of `t`."""
    assert type(shape) is tuple, "Interpolation must be done to a shape"
    return misc.imresize(image, shape, interp='nearest')


def _error_mask(shape, t):
    """"Find a mask that will give the pixels that have error when interpolating up to `shape` by order `t`."""
    m, n, c = shape
    assert c == 3, "The image must have 3 color channels"
    mask = np.ones(m * n, dtype=bool)
    nrow = ceil(n / t)
    ncol = ceil(m / t)
    for i in range(0, nrow * ncol):
        # nrow pixels to be deleted in any row, t pixels between each pixel to be deleted
        irow = (i % nrow) * t
        # t pixels in a row before we go to the next row, t rows to skip with n pixels each
        icol = (i // nrow) * n * t
        mask[irow + icol] = False
    return mask


def error_process(error, t):
    """Process the error matrix to retrieve the pixels from each channel that is expected to have error.

    The error will be split into channels and flattened.
    """
    # Number of pixels to be deleted
    mask = _error_mask(error.shape, t)
    return (error[:,:,0].ravel()[mask],
            error[:,:,1].ravel()[mask],
            error[:,:,2].ravel()[mask])


def _deprocess_error_channel(err, mask, m, n):
    channel = np.zeros(m * n)
    channel[mask] = err
    return channel.reshape((m, n))


def error_deprocess(error, shape, t):
    m, n, c = shape
    e0, e1, e2 = error
    mask = _error_mask(shape, t)
    error = np.empty(shape)
    error[:,:,0] = _deprocess_error_channel(e0, mask, m, n)
    error[:,:,1] = _deprocess_error_channel(e1, mask, m, n)
    error[:,:,2] = _deprocess_error_channel(e2, mask, m, n)
    return error


def compress(image, t=3):
    image = image
    downsampled = downsample(image, t=t)
    rescaled = interpolate(downsampled, image.shape)
    error = error_process(image.astype(np.int16) - rescaled, t=t)
    return zlib.compress(pickletools.optimize(pickle.dumps((downsampled, error))))


def decompress(dump, shape, t=3):
    downsampled, error = pickle.loads(zlib.decompress(dump))
    rescaled = interpolate(downsampled, shape)
    return rescaled + error_deprocess(error, shape, t)
