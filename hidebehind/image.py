import numpy as np
from hidebehind.binutils import bits, set_lsb, set_second_lsb, get_lsb, get_second_lsb, Byte
from hidebehind.secret import Secret
from PIL import Image
from enum import IntEnum


class FormatError(Exception):
    def __init__(self, f):
        super().__init__("The format {} isn't supported yet. The supported ones are {}"
                         .format(f, ImageSecret.SUPPORTED_FORMATS))


class ImageSecret(Secret):
    SUPPORTED_FORMATS = ('PNG', 'GIF')

    class BitsPerPixel(IntEnum):
        one = 0,
        two = 1

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

        # Mode bit + the number of bits in the secret
        b = 1 + len(secret) * 8

        # embed a bit into a pixel
        if b < p:
            mode = ImageSecret.BitsPerPixel.one
        # embed two bits into a pixel
        elif b < p * 2:
            mode = ImageSecret.BitsPerPixel.two
        else:
            raise UserWarning("Your secret is too large for the image to be undetected. "
                              "Try splitting it into parts via *nix command `split(1)`.")

        # We need this to reach every [r, g, b] = A[i][j]
        it = np.ndindex(self.data.shape[:2])
        index = next(it)

        # Save mode bit
        self.data[index][2] = set_lsb(self.data[index][2], int(mode))

        increment = int(mode) + 1
        for byte in secret:
            b_list = bits(byte)
            for j in range(0, len(b_list), increment):
                index = next(it)
                # Set LSB of red to 0
                self.data[index][0] = set_lsb(self.data[index][0], 0)

                blue = self.data[index][2]
                if mode == ImageSecret.BitsPerPixel.two:
                    b1, b0 = b_list[j], b_list[j + 1]
                    b_embedded = set_lsb(set_second_lsb(blue, b1), b0)
                else:
                    b0 = b_list[j]
                    b_embedded = set_lsb(blue, b0)

                self.data[index][2] = b_embedded

        # Indicate the last bit of the secret.
        self.data[index][0] = set_lsb(self.data[index][0], 1)
        return self

    def extract(self) -> bytes:
        """Reads and returns the secret from the image."""
        b_arr = bytearray()

        # Read the sequence of bits from the image. Reconstruct bytes.
        # Stop adding bytes to the array when we encounter a red pixel with LSB set to 1.

        curr_byte = Byte()

        it = np.ndindex(self.data.shape[:2])
        index = next(it)

        mode = ImageSecret.BitsPerPixel.two if get_lsb(self.data[index][2]) == 1 else ImageSecret.BitsPerPixel.one

        for index in it:
            blue = self.data[index][2]

            if mode == self.BitsPerPixel.two:
                b1, b0 = get_second_lsb(blue), get_lsb(blue)
                curr_byte.append(b1)

                if curr_byte.is_full():
                    b_arr.append(curr_byte.value())
                    curr_byte.clear()

                curr_byte.append(b0)
            else:
                b0 = get_lsb(blue)
                curr_byte.append(b0)

            if curr_byte.is_full():
                b_arr.append(curr_byte.value())
                curr_byte.clear()

            red = self.data[index][0]
            if get_lsb(red) == 1:
                return b_arr
