"""The compression algorithm."""

from math import ceil
import logging
import numpy as np
from scipy import misc
from plic import encoding


_LOG = logging.getLogger(__name__)


def downsample(image, t):
    """Downsample an image by skipping `t` pixels."""
    return np.copy(image[::t,::t,:])


def interpolate(image, shape, t):
    """Up-size an image by a factor of `t`."""
    assert type(shape) is tuple, "Interpolation must be done to a shape"
    resized = misc.imresize(image, shape, interp='cubic')
    # Insert the pixels that are certain to be correct
    resized[::t,::t,:] = image
    return resized


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


def _encode_errors(e0, e1, e2):
    code = encoding.build_dictionary(e0, e1, e2)
    e0_enc = encoding.encode(e0, code)
    e1_enc = encoding.encode(e1, code)
    e2_enc = encoding.encode(e2, code)
    _LOG.info(
        "Encoded %s numbers in %s bytes to %s bytes, %s bytes per number on average.",
        len(e0) * 3,
        e0.nbytes * 3,
        len(e0_enc) * 3,
        len(e0_enc) / len(e0),
    )
    return (code, len(e0), e0_enc, e1_enc, e2_enc)


def _decode_errors(error_encoded):
    code, err_len, e0_enc, e1_enc, e2_enc = error_encoded
    return (encoding.decode(e0_enc, code)[:err_len],
            encoding.decode(e1_enc, code)[:err_len],
            encoding.decode(e2_enc, code)[:err_len])


def _encode_image(image):
    data = image.ravel()
    code = encoding.build_dictionary(data)
    return (code, image.shape, encoding.encode(data, code))


def _decode_image(encoded_data):
    code, shape, data = encoded_data
    m, n, c = shape
    image = encoding.decode(data, code)[:m * n * c].reshape(shape)
    return image


def compress(image, t=3):
    downsampled = downsample(image, t=t)
    rescaled = interpolate(downsampled, image.shape, t)
    error = error_process(image.astype(np.int16) - rescaled, t=t)
    error_encoded = _encode_errors(*error)
    return (downsampled, error_encoded, image.shape, t)


def decompress(compressed):
    downsampled, error_encoded, shape, t = compressed
    error = _decode_errors(error_encoded)
    rescaled = interpolate(downsampled, shape, t)
    return rescaled + error_deprocess(error, shape, t)
