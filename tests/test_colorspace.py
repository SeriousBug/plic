from pytest import mark
from skimage import data
from plic import colorspace


class TestColorspace:
    @mark.parametrize('image', [data.astronaut(), data.coffee()])
    def test_colorspace_roundtrip(self, image):
        """Converting from RGB to the RdGdB colorspace, then back to RGB should give the same image."""
        assert (colorspace.rdgdb2rgb(colorspace.rgb2rdgdb(image)) == image).all()
