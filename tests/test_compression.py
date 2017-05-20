from pytest import mark
from plic import compression


from .test_base import TEST_IMAGES


class TestCompression:

    @mark.parametrize('image', TEST_IMAGES)
    def test_compression_roundtrip(self, image):
        """Compressing then decompressing an image should give back the same image."""
        assert (compression.CompressedImage(image).reconstruct() == image).all()
