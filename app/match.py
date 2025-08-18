import compile
import string

ALPHANUMERIC = set(string.ascii_letters + string.digits + "_")

def match_recursive(pattern, input_line, p_ind=0, l_ind=0):
    """
        Recursively matches pattern with the given input string.
        args:
            pattern: List[RE_Pattern] - list of singular regular expression patterns
            input_line: str - string to be matched with pattern
            p_ind: int - current position in pattern array
            l_ind: int - current position in input string

        returns:
            matched: bool - True is input string matches given pattern
    """
    # Base cases
    if p_ind >= len(pattern): return True
    if l_ind >= len(input_line): return False

    matched = False # we can't just return since we also should consider options

    curr_pattern = pattern[p_ind]
    # continue
    if curr_pattern.pattern_type == compile.OPTION:
        return match_recursive(pattern, input_line, p_ind+1, l_ind)

    next_pattern = pattern[p_ind + 1] if p_ind < len(pattern) - 1 else None

    curr_char = input_line[l_ind]

    if curr_pattern.pattern_type == compile.CHAR:
        if curr_pattern.pattern == curr_char:
            matched |=  match_recursive(pattern, input_line, p_ind+1, l_ind+1)
    elif curr_pattern.pattern_type == compile.METACHAR:
        if curr_pattern.pattern == r"\w":
            if curr_char in ALPHANUMERIC:
                matched |=  match_recursive(pattern, input_line, p_ind+1, l_ind+1)
        elif curr_pattern.pattern == r"\d":
            if curr_char.isnumeric():
                matched |=  match_recursive(pattern, input_line, p_ind+1, l_ind+1)
        else:
            raise(Exception(f"Unknown metacharacter {curr_pattern.pattern}"))
    elif curr_pattern.pattern_type == compile.GROUP:
        is_match = False

        for subpattern in curr_pattern.pattern_list:
            is_match |= match_recursive([subpattern], curr_char)

        # if negation, then negation ^ is_match = not is_match
        # if true, continue, else return False
        if curr_pattern.negation ^ is_match: 
            matched |=  match_recursive(pattern, input_line, p_ind+1, l_ind+1)

    if next_pattern and next_pattern.pattern_type == compile.OPTION:
        # up to this point we have tried to match one time (and probably have failed)
        # thus we can try to match depending on option provided
        if next_pattern.pattern == "+":
            matched |=  match_recursive(pattern, input_line, p_ind, l_ind+1) # matches multiple times
        elif next_pattern.pattern == "?":
            matched |=  match_recursive(pattern, input_line, p_ind+2, l_ind) # skip current pattern

    return matched


def match(pattern_list, input_line):
    if len(pattern_list) != len(input_line): return False

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
                is_match |= match([sub_re], curr_char)

            if not (re.negation ^ is_match): # if negation is True, just negates is_match
                return False

    return True

if __name__ == "__main__":
    tests = [
            (r"abc", "abc"),
            (r"a[abc]c", "abc"),
            (r"\d[0\w][^dg]", "1ad"),
            (r"abc", "a"),
            (r"[^abc]+\w?", "ddd"),
            (r"\d+a", "12345a"),
            (r"\d+a", "12345"),
            (r"\d+a", "12a"),
            (r"\d+a", "45a"),
            ]

    for p, s in tests:
        pattern_list = compile.parse_all(p)

        print(match_recursive(pattern_list, s))
