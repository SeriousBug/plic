from pytest import mark
from plic import colorspace

from .test_base import TEST_SOURCE


class TestColorspace:
    @mark.parametrize('image', TEST_SOURCE)
    def test_colorspace_roundtrip(self, image):
        """Converting from RGB to the RdGdB colorspace, then back to RGB should give the same image."""
        assert (colorspace.rdgdb2rgb(colorspace.rgb2rdgdb(image)) == image).all()
