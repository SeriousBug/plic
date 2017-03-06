from collections import Counter
import itertools
from bitarray import bitarray
import huffman
import numpy as np


def _dict_makebit(dictionary):
    """`huffman.codebook` function gives regular strings as values. Convert them to bitarrays."""
    return {k: bitarray(v) for k, v in dictionary.items()}


def build_dictionary(*arrays):
    """Build a huffman encoding dictionary that can encode the data in given arrays."""
    return _dict_makebit(huffman.codebook(Counter(itertools.chain(*arrays)).items()))


def encode(array, dictionary):
    """Encode the data in `array` using the huffman `dictionary`."""
    b = bitarray(endian='little')
    b.encode(dictionary, array)
    # toBytes inserts extra 0's to the end, trim them!
    return b.tobytes()


def decode(encoded, dictionary):
    """Decode the `encoded` data into a numpy array using the huffman `dictionary`."""
    b = bitarray(endian='little')
    b.frombytes(encoded)
    return np.array(b.decode(dictionary))
