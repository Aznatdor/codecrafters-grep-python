import compile
import string

ALPHANUMERIC = set(string.ascii_letters + string.digits + "_")

def match(pattern, input_line):
    pattern_list = compile.parse_all(pattern)

    if len(pattern_list) != len(input_line): return 0

    length = len(pattern_list)

    for i in range(length):
        re, curr_char = pattern_list[i], input_line[i]

        if re.pattern_type == compile.CHAR:
            if re.pattern != curr_char:
                return False
        elif re.pattern_type == compile.METACHAR:
            if re.pattern == "\\d":
                if not curr_char.isnumeric():
                    return False
            if re.pattern == "\\w":
                if curr_char not in ALPHANUMERIC:
                    return False
        elif re.pattern_type == compile.GROUP:
            is_match = False

            for sub_re in re.pattern_list:
                is_match |= match(r"{}".format(sub_re.pattern), curr_char)

            if not (re.negation ^ is_match): # if negation is True, just negates is_match
                return False

    return True

if __name__ == "__main__":
    print(match(r"abc", "abc"))
    print(match(r"a[abc]c", "abc"))
    print(match(r"\d[0\w][^dg]", "1ad"))
