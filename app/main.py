import sys
import string
# import pyparsing - available if you need it!
# import lark - available if you need it!

# ======================== preprocessing functions ==========================================

# Preprocessing step for grep
# Parses input string into sequence of special characters without verifying if the sequence makes sense and etc

CHAR = 1
METACHAR = 2
GROUP = 3
ANCHOR = 4
OPTION = 5

class RE_Pattern:
    def __init__(self, pattern_type, pattern, pattern_list=[], negation=False):
        self.pattern_type = pattern_type
        self.pattern = pattern
        self.pattern_list = pattern_list
        self.negation = negation

    def __str__(self):
        return f"\nType: {self.pattern_type}\nPattern: {self.pattern}\nList: {self.pattern_list}\nNegation: {self.negation}"

    def __repr__(self):
        return f"\nType: {self.pattern_type}\nPattern: {self.pattern}\nList: {self.pattern_list}\nNegation: {self.negation}"


def parse(pattern, ind=0):
    # Parse one RE character
    # For convinience also returns the index where the next pattern should begin
    curr_ind = ind
    times = 0

    while True:
        # Parse metachar
        if pattern[curr_ind] == "\\":
            if curr_ind < len(pattern) - 1: curr_ind += 1
            else: return None, None
            
            # Might be just a simple "\" character
            if pattern[curr_ind] == "\\":
                return RE_Pattern(CHAR, "\\"), curr_ind + 1

            # some metachar
            return RE_Pattern(METACHAR, "\\" + pattern[curr_ind]), curr_ind + 1
        elif pattern[curr_ind] in ["+", "*", "?"]:
            return RE_Pattern(OPTION, pattern[curr_ind]), curr_ind + 1
        # Parse group
        elif pattern[curr_ind] == "[":
            group = []
            if curr_ind < len(pattern) - 1: curr_ind += 1
            else: return None, None
            
            negation = pattern[curr_ind] == "^"
            if negation: curr_ind += 1

            # get the subpattern within the group and parse it into the list
            pattern_end = pattern.find("]", curr_ind)
            subpattern = pattern[curr_ind : pattern_end]

            group = parse_all(subpattern)
            return RE_Pattern(GROUP, None, group, negation=negation), pattern_end + 1

        elif pattern[curr_ind] == "^":
            return RE_Pattern(ANCHOR, "^"), curr_ind + 1
        elif pattern[curr_ind] == "$":
            return RE_Pattern(ANCHOR, "$"), curr_ind + 1
        else: # Parse simple char
            return RE_Pattern(CHAR, pattern[curr_ind]), curr_ind + 1


def parse_all(pattern):
    """
        Splits pattern into individual regex patterns

        Args:
            pattern: str

        Returns:
            pattern_list: List[RE_Pattern]
    """

    curr_ind = 0
    pattern_list = []
    while curr_ind != len(pattern): 
        re, next_ind = parse(pattern, curr_ind) 
        curr_ind = next_ind
        pattern_list.append(re)

    return pattern_list


# =================================== main matching function ==========================

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
    if curr_pattern.pattern_type == OPTION:
        return match_recursive(pattern, input_line, p_ind+1, l_ind)

    next_pattern = pattern[p_ind + 1] if p_ind < len(pattern) - 1 else None

    curr_char = input_line[l_ind]

    if curr_pattern.pattern_type == CHAR:
        if curr_pattern.pattern == curr_char:
            matched |=  match_recursive(pattern, input_line, p_ind+1, l_ind+1)
    elif curr_pattern.pattern_type == METACHAR:
        if curr_pattern.pattern == r"\w":
            if curr_char in ALPHANUMERIC:
                matched |=  match_recursive(pattern, input_line, p_ind+1, l_ind+1)
        elif curr_pattern.pattern == r"\d":
            if curr_char.isnumeric():
                matched |=  match_recursive(pattern, input_line, p_ind+1, l_ind+1)
        else:
            raise(Exception(f"Unknown metacharacter {curr_pattern.pattern}"))
    elif curr_pattern.pattern_type == GROUP:
        is_match = False

        for subpattern in curr_pattern.pattern_list:
            is_match |= match_recursive([subpattern], curr_char)

        # if negation, then negation ^ is_match = not is_match
        # if true, continue, else return False
        if curr_pattern.negation ^ is_match: 
            matched |=  match_recursive(pattern, input_line, p_ind+1, l_ind+1)

    if next_pattern and next_pattern.pattern_type == OPTION:
        # up to this point we have tried to match one time (and probably have failed)
        # thus we can try to match depending on option provided
        if next_pattern.pattern == "+":
            matched |=  match_recursive(pattern, input_line, p_ind, l_ind+1) # matches multiple times
        elif next_pattern.pattern == "?":
            matched |=  match_recursive(pattern, input_line, p_ind+2, l_ind) # skip current pattern

    return matched


def main():
    pattern = sys.argv[2]
    pattern_list = parse_all(pattern)
    input_line = sys.stdin.read()


    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    input_len = len(input_line)

    if pattern_list[0].pattern == "^":
        if match_recursive(pattern_list[1:], input_line):
            exit(0)
        exit(1)

    if pattern_list[-1].pattern ==  "$":
        pattern_len = len(pattern_list) - 1
        if match_recursive(pattern_list[:-1], input_line[-pattern_len:]):
            exit(0)
        exit(1)


    for start_pos in range(input_len):
        if match_recursive(pattern_list, input_line, l_ind=start_pos):
            # print(True)
            exit(0)

    exit(1)
    return 
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)


if __name__ == "__main__":
    main()
