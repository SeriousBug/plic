from pytest import mark
from skimage import data
from plic import colorspace, compression


t = 3
test_images = list(map(colorspace.rgb2rdgdb, [data.astronaut(), data.coffee()]))
test_errors = list(map(lambda i: i - compression.interpolate(compression.downsample(i, t), i.shape), test_images))


class TestCompression:
    @mark.parametrize('error', test_errors)
    def test_error_process_roundtrip(self, error):
        """The error matrix should be the same after processing and deprocessing."""
        assert (compression.error_deprocess(compression.error_process(error, t), error.shape, t) == error).all()

    @mark.parametrize('error', test_errors)
    def test_mask_errorfree(self, error):
        """The error in pixels skipped by the error mask should be 0."""
        inverse_mask = ~(compression._error_mask(error.shape, t))
        assert (error[:,:,0].ravel()[inverse_mask] == 0).all()
        assert (error[:,:,1].ravel()[inverse_mask] == 0).all()
        assert (error[:,:,2].ravel()[inverse_mask] == 0).all()

    @mark.parametrize('image', test_images)
    def test_compression_roundtrip(self, image):
        """Compressing then decompressing an image should give back the same image."""
        assert (compression.decompress(compression.compress(image), image.shape) == image).all()
