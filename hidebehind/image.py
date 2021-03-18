import numpy as np
from hidebehind.binutils import bits, set_lsb, get_lsb
from hidebehind.secret import Secret
from PIL import Image

# TODO: save storing mode (2bits->pixel OR bit->pixel)


class FormatError(Exception):
    def __init__(self, f):
        super().__init__("The format {} isn't supported yet. The supported ones are {}"
                         .format(f, ImageSecret.SUPPORTED_FORMATS))


class ImageSecret(Secret):
    SUPPORTED_FORMATS = ('PNG', 'GIF')

    def load(self, filename):
        """Loads pixels from the image `filename`.

        :param filename: A filename string or a file object (opened in 'b' mode).
        """
        img = Image.open(filename)
        self.format = img.format

        if self.format not in ImageSecret.SUPPORTED_FORMATS:
            raise FormatError(self.format)

        self.data = np.array(img.convert('RGBA'))

    def save(self, filename):
        """Saves the image. See also ImageSecret.load()"""
        img = Image.fromarray(self.data, mode='RGBA')
        img.save(filename, self.format)

    def embed(self, secret: bytes):
        """Embeds `secret` into the image.

        :param secret: A secret message to be embedded into the image.
        :returns itself, so that it's possible to write `ImageSecret('f.png').embed(b'abc').save('f-embedded.png')`
        """

        # The number of pixels in the image
        p = self.data.shape[0] * self.data.shape[1]

        # The number of bits in the secret
        b = len(secret) * 8

        # TODO: refactor.
        bits_per_pixel = None
        # embed a bit into a pixel
        if b < p:
            bits_per_pixel = 1

        # embed two bits into a pixel
        elif b < p * 2:
            bits_per_pixel = 2
        else:
            # TODO: test whether changing 2+ channels in image can be seen.
            raise UserWarning("Your secret is too large for the image to be undetected. "
                              "Try splitting it into parts via *nix command `split(1)`.")

        # We need this to reach every [r, g, b] = A[i][j]
        it = np.ndindex(self.data.shape[:2])
        index = None

        for byte in secret:
            # TODO: refactor. Consider the case when we embed 2 bits into one pixel.
            for bit in bits(byte):
                # TODO: refactor. White a wrapper that returns None instead of raising an exception.
                try:
                    index = next(it)
                except StopIteration:
                    break

                blue = self.data[index][2]
                b_embedded = set_lsb(blue, bit)

                self.data[index][2] = b_embedded

                # Set LSB of red's to 0
                self.data[index][0] = set_lsb(self.data[index][0], 0)

        try:
            index = next(it)
        except StopIteration:
            raise Exception("")

        self.data[index][0] = set_lsb(self.data[index][0], 1)

        return self

    def extract(self) -> bytes:
        """Reads and returns the secret from the image."""
        b_arr = bytearray()

        # Read the sequence of bits from the image. Reconstruct bytes.
        # Stop adding bytes to the array when we encounter a red pixel with LSB set to 1.

        current_byte = 0
        bit_power = 7

        # We need this to reach every [r, g, b] = A[i][j]
        for index in np.ndindex(self.data.shape[:2]):
            if bit_power < 0:
                bit_power = 7
                b_arr.append(current_byte)
                current_byte = 0

            red = self.data[index][0]
            if get_lsb(red) == 1:
                break

            blue = self.data[index][2]
            lsb = get_lsb(blue)

            current_byte |= lsb << bit_power
            bit_power -= 1

        return b_arr
