def bits(n: int):
    """Returns a list of bits in the byte `n`.
    :param n: a byte (8 bits) in [0; 256)

    For example, bits(5) = [0, 0, 0, 0, 0, 1, 0, 1], because 5_10 = 101_2
    """
    assert 0 <= n < 256

    result = []
    for i in range(8)[::-1]:
        if n & (1 << i):
            result.append(1)
        else:
            result.append(0)
    return result


def set_lsb(n: int, b: int):
    """Sets least significant bit of `n` to `b`"""
    assert 0 <= n < 256 and b in (0, 1)

    # We want n to have the bit `b` at the end of it.
    # For example, if the bit is 1 and n is 110, we change n to 111 and vise versa.
    # If the bit is 1 and n is 101, we change nothing. The same for 0.

    # To understand what `n & ~1` means for consider an example:
    #      n = 11011001
    #     ~1 = 11111110
    # ~1 & n = 11011000
    # The last is bit-by-bit the same as n except the last bit. The last one was cleared.
    # Hooray, by doing this we solved a half of the problem =)

    # When we have a number with the least-significant-bit cleared, we can put anything (1 or 0)
    # there by ORing the number with the bit we want to put.
    # For example,
    #         ~1 & b = 11011000
    #            bit = 00000001
    # (~1 & b) | bit = 11011001

    return (n & ~1) | b


def set_second_lsb(n: int, b: int):
    """See also set_lsb()"""
    return (n & ~2) | (b << 1)


def get_lsb(n: int) -> int:
    """Returns the least significant bit of n"""
    return n & 1


def get_second_lsb(n: int) -> int:
    """See also get_lsb()"""
    return (n & 2) >> 1


class Byte:
    def __init__(self):
        self.power = 7
        self.val = 0

    def value(self):
        return self.val

    def append(self, b: int):
        self.val |= (b << self.power)
        self.power -= 1

    def is_full(self) -> bool:
        return self.power < 0

    def clear(self):
        self.__init__()
