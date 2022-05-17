import typing


def transform_number_big_endian(inp: typing.List[int]) -> typing.List[str]:
    max_len = max((abs(num).bit_length() for num in inp))
    res: typing.List[str] = []

    for inp_item in inp:
        inp_bin = bin(abs(inp_item))[2:].rjust(max_len+1, "0")

        if inp_item < 0:
            inp_bin_a = ""
            found_1 = False

            for bit in reversed(inp_bin):
                if bit == "0" and not found_1:
                    inp_bin_a = bit + inp_bin_a

                elif bit == "1" and not found_1:
                    inp_bin_a = bit + inp_bin_a
                    found_1 = True

                else:
                    inp_bin_a = str(1 - int(bit)) + inp_bin_a

            inp_bin = inp_bin_a

        res.append(inp_bin)

    return res

def transform_numbers_little_endian(inp: typing.List[int]) -> typing.List[str]:
    max_len = max((abs(num).bit_length() for num in inp))
    reversing_num = 1 << max_len
    return [bin(num)[:1:-1].ljust(max_len, "0") + "0" if num >= 0 else bin(reversing_num - abs(num))[:1:-1].ljust(max_len, "0") + "1" for num in inp]