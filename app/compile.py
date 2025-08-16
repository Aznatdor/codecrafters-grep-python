import string

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
        # Parse simple char
        elif pattern[curr_ind] in ["+", "*", "?"]:
            return RE_Pattern(OPTION, pattern[curr_ind]), curr_ind + 1
        elif pattern[curr_ind].isalpha():
            return RE_Pattern(CHAR, pattern[curr_ind]), curr_ind + 1
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


if __name__ == "__main__":
    pattern =r"a+\w?^c\\[^abc\d]*$" 
    res = parse_all(pattern)
    print(pattern)
    print(res)
