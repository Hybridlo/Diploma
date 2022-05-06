import typing


def transform_number(inp: int) -> typing.Tuple[str, str]:
    return "1" if inp < 0 else "0", bin(inp)[2:]