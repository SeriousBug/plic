from pytest import mark
from plic import compression


from .test_base import T, TEST_ERRORS, TEST_IMAGES


class TestCompression:
    @mark.parametrize('error', TEST_ERRORS)
    def test_error_process_roundtrip(self, error):
        """The error matrix should be the same after processing and deprocessing."""
        assert (compression.error_deprocess(compression.error_process(error, T), error.shape, T) == error).all()

    @mark.parametrize('error', TEST_ERRORS)
    def test_mask_errorfree(self, error):
        """The error in pixels skipped by the error mask should be 0."""
        inverse_mask = ~(compression._error_mask(error.shape, T))
        assert (error[:,:,0].ravel()[inverse_mask] == 0).all()
        assert (error[:,:,1].ravel()[inverse_mask] == 0).all()
        assert (error[:,:,2].ravel()[inverse_mask] == 0).all()

    @mark.parametrize('image', TEST_IMAGES)
    def test_compression_roundtrip(self, image):
        """Compressing then decompressing an image should give back the same image."""
        assert (compression.decompress(compression.compress(image)) == image).all()
