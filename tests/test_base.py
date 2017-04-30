from skimage import data
from plic import colorspace, compression


T = 3
TEST_SOURCE = [data.astronaut(), data.coffee(), data.chelsea(), data.rocket()]
TEST_IMAGES = list(map(colorspace.rgb2rdgdb, TEST_SOURCE))
TEST_ERRORS = list(map(lambda i: i - compression.interpolate(compression.downsample(i, T), i.shape, T), TEST_IMAGES))
