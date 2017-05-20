from skimage import data
from plic import colorspace


TEST_SOURCE = [data.astronaut(), data.coffee(), data.chelsea(), data.rocket()]
TEST_IMAGES = list(map(colorspace.rgb2rdgdb, TEST_SOURCE))
