import sys
import string
import functools
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
ALTERNATION = 6

class RE_Pattern:
    def __init__(self, pattern_type, pattern, pattern_list=[], negation=False):
        self.pattern_type = pattern_type
        self.pattern = pattern
        self.pattern_list = pattern_list
        self.negation = negation

    def __str__(self):
        return f" Type: {self.pattern_type} Pattern: {self.pattern} List:\n{self.pattern_list} Negation: {self.negation}"

    def __repr__(self):
        return f" Type: {self.pattern_type} Pattern: {self.pattern} List:\n{self.pattern_list} Negation: {self.negation}"

    def __eq__(self, t):
        return (self.pattern_type == t.pattern_type and
                self.pattern == t.pattern and
                self.pattern_list == t.pattern_list and
                self.negation == t.negation)


# ========================== parsing functions =================================================

def find_end(pattern, start=0):
    """
        args:
            pattern: str - group-string starting with )

        returns:
            end: int - index for matching closing )
    """
    pattern = pattern[start:]

    depth = 0
    for i, c in enumerate(pattern):
        if c == "(": depth += 1
        if c == ")": depth -= 1
        if depth == 0: return i + start

    raise(ValueError("Unmatched parentheses"))


def split_group(pattern):
    """
        args:
            pattern: str - group-string

        returns:
            group: list - list of subpatterns within the main pattern
    """

    depth = 0
    group = []
    curr = ""

    for c in pattern:
        if c == "(":
            depth += 1
            if depth > 1:
                curr += "("
        elif c == ")":
            depth -= 1
            if depth > 0:
                curr += ")"
        elif c == "|":
            if depth == 1:
                group.append(curr)
                curr = ""
            else:
                curr += "|"
        else:
            curr += c

    if curr: group.append(curr)

    if depth > 0: raise(ValueError("Unmatched parentheses"))

    return group


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
            return RE_Pattern(GROUP, None, group, negation), pattern_end + 1
        elif pattern[curr_ind] == "(":
            pattern_end = find_end(pattern, curr_ind)
            group = pattern[curr_ind:pattern_end+1] # list of subpattern within the "main" group pattern. ")" should be inclusive

            options_raw = split_group(group)

            # parse_all would get some pattern, maybe, of the form "(something)
            options = list(map(parse_all, options_raw))
            return RE_Pattern(ALTERNATION, None, options), pattern_end + 1

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


# =================================== main matching class  ==========================

ALPHANUMERIC = set(string.ascii_letters + string.digits + "_")

cnt = [0]

class Matcher:
    def __init__(self, pattern, input_line):
        self.input_line = input_line
        self.pattern = pattern


    @functools.cache
    def match_recursive(self, p_ind=0, l_ind=0):
        """
            Recursively matches pattern with the given input string.
            args:
                p_ind: int - current position in pattern array
                l_ind: int - current position in input string

            returns:
                matched: bool - True is input string matches given pattern
                l_ind: int - index where we have finished matching or -1  otherwise
        """
        if cnt[0] == 100: raise(RuntimeError("Infinity"))
        cnt[0] += 1
        print(cnt[0])

        # Base cases
        if p_ind >= len(self.pattern): 
            print("TRUE", l_ind)
            return (True, l_ind)
        if l_ind >= len(self.input_line): 
            return (False, -1)

        matched = False # we can't just return since we also should consider options
        return_ind = -1

        curr_pattern = self.pattern[p_ind]
        # continue
        if curr_pattern.pattern_type == OPTION:
            return  self.match_recursive(p_ind+1, l_ind) # we should just continue, thus return what the next iteration returns

        next_pattern = self.pattern[p_ind + 1] if p_ind < len(self.pattern) - 1 else None

        curr_char = self.input_line[l_ind]
        
        if curr_pattern.pattern == ".":
            if curr_pattern.pattern == curr_char:
                res, ind = self.match_recursive(p_ind+1, l_ind+1)
                if res:
                    matched = True
                    return_ind = ind
        elif curr_pattern.pattern_type == CHAR:
            if curr_pattern.pattern == curr_char:
                res, ind = self.match_recursive(p_ind+1, l_ind+1)
                if res:
                    matched = True
                    return_ind = ind
        elif curr_pattern.pattern_type == METACHAR:
            if curr_pattern.pattern == r"\w":
                if curr_char in ALPHANUMERIC:
                    res, ind = self.match_recursive(p_ind+1, l_ind+1)
                    if res:
                        matched = True
                        return_ind = ind
            elif curr_pattern.pattern_type == METACHAR:
                    res, ind = self.match_recursive(p_ind+1, l_ind+1)
                    if res:
                        matched = True
                        return_ind = ind
            elif curr_pattern.pattern == r"\d":
                if curr_char.isnumeric():
                    res, ind = self.match_recursive(p_ind+1, l_ind+1)
                    if res:
                        matched = True
                        return_ind = ind
            elif curr_pattern.pattern == r"\d":
                    res, ind = self.match_recursive(p_ind+1, l_ind+1)
                    if res:
                        matched = True
                        return_ind = ind
            else:
                raise(Exception(f"Unknown metacharacter {curr_pattern.pattern}"))
        elif curr_pattern.pattern_type == GROUP:
            is_match = False

            for subpattern in curr_pattern.pattern_list:
                option_matcher = Matcher([subpattern], curr_char)
                is_match |= option_matcher.match_recursive()[0]

            # if negation, then negation ^ is_match = not is_match
            # if true, continue, else return False
            if curr_pattern.negation ^ is_match: 
                res, ind = self.match_recursive(p_ind+1, l_ind+1)
                if res:
                    matched = True
                    return_ind = ind

        elif curr_pattern.pattern_type == ALTERNATION:
            is_match = False

            for subpattern in curr_pattern.pattern_list:
                # If we have something like (abc|bca)+, we should consider abc(abc|bca)+ and bca(abc|bca)+
                # as well as just abc, bca and abcabc, abcbca... 
                if next_pattern and next_pattern.pattern == "+":
                    # first case is unwrap one iteration of ()+, i.e. ()()+ case

                    # try to match current pattern at least once. To avoid infinite recurrsion
                    test_matcher = Matcher(subpattern, self.input_line)
                    _, new_ind = test_matcher.match_recursive(l_ind=l_ind)

                    # I think here we can just return since we already are considering options
                    if new_ind > l_ind: # if matched, continue. We might skip the next iteration or continue on recurring
                        res, ind = self.match_recursive(p_ind=p_ind, l_ind=new_ind) # pattern[p_ind:] consists of the current pattern (which is (group)) and the rest of the pattern
                        print("ALT", res, ind)
                        if res: return (True, ind)

                    # stop iterations
                    res, ind = self.match_recursive(p_ind+2, l_ind) # we could create new Matcher, but I though since we 
                                                                            # are just skip two positions in pattern, we might use self

                    print("ALT SKIP", res, ind)
                    
                    if res:
                        return (True, ind)

                # if we have (ab|bc)? we should check ab, bc or just skip
                else:
                    #  check for both "simple" case and "?" cases
                    simple_matcher = Matcher(subpattern + self.pattern[p_ind+2:], self.input_line)
                    res, ind = simple_matcher.match_recursive(l_ind=l_ind)
                    if res: return (True, ind)

                    # skip if we have "?" case
                    if next_pattern and next_pattern.pattern == "?":
                        # skip_matcher = Matcher(self.pattern[p_ind+2:], self.input_line)
                        res, ind =  self.match_recursive(p_ind+2, l_ind)

                        if res: return (True, ind)

            return (False, -1) # If we have found a match we have matched the whole string, so we can easily return True

        elif curr_pattern.pattern == "$":
            if self.input_line[l_ind] == "\0": 
                return (True, l_ind-1) # we should not account the EOF character. Also can just return
            return (False, -1)
        
        if curr_pattern.pattern_type != ALTERNATION and next_pattern and next_pattern.pattern_type == OPTION:
            # up to this point we have tried to match one time (and probably have failed)
            # thus we can try to match depending on option provided
            if next_pattern.pattern == "+":
                res, ind = self.match_recursive(p_ind, l_ind+1) # matches multiple times
                if res: return (True, ind)
            elif next_pattern.pattern == "?":
                res, ind = self.match_recursive(p_ind+2, l_ind) # skip current pattern
                if res: return (True, ind)

        return (matched, return_ind)


def main():
    pattern = sys.argv[2]
    pattern_list = parse_all(pattern)
    input_line = sys.stdin.read()

    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    input_len = len(input_line)

    if pattern_list[-1].pattern == "$": # add EOF char. Then, we should check the condition "$" == EOF
        input_line += "\0"

    if pattern_list[0].pattern == "^":
        matcher = Matcher(pattern_list[1:], input_line)
        res, ind = matcher.match_recursive()
        if res:
            print(True, ind)
            exit(0)
        print(False)
        exit(1)

    matcher = Matcher(pattern_list, input_line)

    for start_pos in range(input_len):
        res, ind = matcher.match_recursive(l_ind=start_pos)
        if res:
            print(True, ind)
            exit(0)
    
    print(False)
    exit(1)
    return 
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)


if __name__ == "__main__":
    print(parse_all("((abc)(def))") == parse_all("((abc)|(def))"))
    main()
