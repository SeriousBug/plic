"""The compression algorithm."""

from math import ceil, floor, log2
import logging
import numpy as np
from scipy import misc
from plic import encoding

_LOG = logging.getLogger(__name__)


class EncodedError:
    @staticmethod
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

    def __init__(self, error, ratio):
        """Encode an error matrix that was created after a `ratio` downsampling."""
        self.shape = error.shape
        self.ratio = ratio
        mask = self._error_mask(self.shape, ratio)
        channels = (
            error[:,:,0].ravel()[mask],
            error[:,:,1].ravel()[mask],
            error[:,:,2].ravel()[mask],
        )
        self.code = encoding.build_dictionary(*channels)
        self.encoded = []
        for channel in channels:
            self.encoded.append(encoding.encode(channel, self.code))
        _LOG.info(
            "Error encoding: encoded %s bytes to %s bytes",
            sum(map(lambda c: c.nbytes, channels)),
            sum(map(lambda e: len(e), self.encoded)),
        )

    def _deprocess_error_channel(self, err, mask):
        """Insert the deleted zeroes into the error channels."""
        m, n, _ = self.shape
        channel = np.zeros(m * n)
        channel[mask] = err
        return channel.reshape((m, n))

    def reconstruct(self):
        """Convert the encoded error back to the error matrix."""
        m, n, _ = self.shape
        mask = self._error_mask(self.shape, self.ratio)
        error = np.empty(self.shape)
        for i, channel in enumerate(self.encoded):
            decoded = encoding.decode(channel, self.code)[:m * n - 1]
            error[:,:,i] = self._deprocess_error_channel(decoded, mask)
        return error


class EncodedImage:
    def __init__(self, image):
        """Encode an image with Huffman encoding."""
        data = image.ravel()
        self.shape = image.shape
        self.code = encoding.build_dictionary(data)
        self.encoded = encoding.encode(data, self.code)
        _LOG.info(
            "Image encoding: encoded %s bytes to %s bytes",
            data.nbytes,
            len(self.encoded)
        )

    def reconstruct(self):
        """Convert the encoded image back to the original matrix form."""
        m, n, c = self.shape
        image = encoding.decode(self.encoded, self.code)[:m * n * c].reshape(self.shape)
        return image


class CompressedImage:
    @staticmethod
    def downsample(image, t):
        """Downsample an image by skipping `t` pixels."""
        return np.copy(image[::t,::t,:])

    @staticmethod
    def interpolate(image, shape, t):
        """Up-size an image to size of `shape`."""
        assert type(shape) is tuple, "Interpolation must be done to a shape"
        resized = misc.imresize(image, shape, interp='cubic')
        # Insert the pixels that are certain to be correct
        resized[::t,::t,:] = image
        return resized

    def __init__(self, image, times=0, ratio=2):
        """Compress an image.

        The compression operation will be performed recursively. The
        depth of the recursion is determined by `times` parameter. If
        `times` is 0, the recursion depth is determined automatically.
        With each recursion, the downsampled form of the image is
        compressed again using the algorithm.

        Ratio is the downsampling ratio. Higher values are better for
        less detailed images.
        """
        if times == 0:
            m, n, _ = image.shape
            times = floor(min(log2(m / 256), log2(n / 256)))
        self.times = times
        self.ratio = ratio
        self.shape = image.shape
        downsampled = self.downsample(image, t=ratio)
        rescaled = self.interpolate(downsampled, image.shape, ratio)
        self.error = EncodedError(image.astype(np.int32) - rescaled, ratio)
        # If we're not recursing anymore, store the actual downsampled image
        if self.times <= 1:
            self.downsampled = EncodedImage(downsampled)
        else:
            self.downsampled = CompressedImage(downsampled, times - 1, ratio)

    def reconstruct(self):
        """Decompress the image."""
        downsampled = self.downsampled.reconstruct()
        error = self.error.reconstruct()
        rescaled = self.interpolate(downsampled, self.shape, self.ratio)
        return rescaled + error
