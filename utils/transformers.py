import typing


def transform_number_big_endian(inp: int) -> typing.Tuple[str, str]:
    return "1" if inp < 0 else "0", bin(inp)[2:]

def transform_numbers_little_endian(inp: typing.List[int]) -> typing.List[str]:
    max_len = max((abs(num).bit_length() for num in inp))
    reversing_num = 1 << max_len
    return [bin(num)[:1:-1].ljust(max_len, "0") + "0" if num >= 0 else bin(reversing_num - abs(num))[:1:-1].ljust(max_len, "0") + "1" for num in inp]