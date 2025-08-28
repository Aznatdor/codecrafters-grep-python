import sys
import os
from pathlib import Path
import string
import functools

# ======================== preprocessing functions ==========================================

# Preprocessing step for grep
# Parses input string into sequence of special characters without verifying if the sequence makes sense and etc

CHAR = 1
METACHAR = 2
GROUP = 3
ANCHOR = 4
OPTION = 5
ALTERNATION = 6
BACKREFERRENCE = 7

BACKREFERRENCE_LIST = dict()
NUM_GROUPS = 0

class RE_Pattern:
    def __init__(self, pattern_type, pattern, pattern_list=[], negation=False, group_num=0):
        self.pattern_type = pattern_type
        self.pattern = pattern
        self.pattern_list = pattern_list
        self.negation = negation

        self.group_num = group_num

    def __str__(self):
        return f" Type: {self.pattern_type} Pattern: {self.pattern} List:\n{self.pattern_list} Negation: {self.negation}"

    def __repr__(self):
        return f" Type: {self.pattern_type} Pattern: {self.pattern} List:\n{self.pattern_list} Negation: {self.negation}\nInd: {self.group_num}"

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
    global NUM_GROUPS
    curr_ind = ind

    while True:
        # Parse metachar
        if pattern[curr_ind] == "\\":
            if curr_ind < len(pattern) - 1: curr_ind += 1
            else: return None, None
            
            # Might be just a simple "\" character
            if pattern[curr_ind] == "\\":
                return RE_Pattern(CHAR, "\\"), curr_ind + 1
            elif pattern[curr_ind].isnumeric():
                num = ""
                while curr_ind < len(pattern) and pattern[curr_ind].isnumeric():
                    num += pattern[curr_ind]
                    curr_ind += 1
                return RE_Pattern(BACKREFERRENCE, int(num)), curr_ind # since curr_ind is already in the beginning of the next pattern

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
            NUM_GROUPS += 1
            curr_num = NUM_GROUPS
            pattern_end = find_end(pattern, curr_ind)
            group = pattern[curr_ind:pattern_end+1] # list of subpattern within the "main" group pattern. ")" should be inclusive

            options_raw = split_group(group)

            # parse_all would get some pattern, maybe, of the form "(something)
            options = list(map(parse_all, options_raw))
            return RE_Pattern(ALTERNATION, None, options, group_num=curr_num), pattern_end + 1

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
        if cnt[0] == 1000: raise(RuntimeError("Infinity"))
        cnt[0] += 1

        matched = False # we can't just return since we also should consider options
        return_ind = -1
        next_pattern = self.pattern[p_ind + 1] if p_ind < len(self.pattern) - 1 else None


        # we should be able to skip current pattern in the end of the string
        if next_pattern and  next_pattern.pattern == "?":
            res, ind = self.match_recursive(p_ind+2, l_ind) # skip current pattern
            if res:
                matched = True
                return_ind = ind

        # Base cases
        if p_ind >= len(self.pattern): 
            return (True, l_ind)
        if l_ind >= len(self.input_line):
            if matched:
                return (True, min(len(self.input_line) - 1, l_ind))
            return (False, -1)

        curr_pattern = self.pattern[p_ind]

        # continue
        if curr_pattern.pattern_type == OPTION:
            return self.match_recursive(p_ind+1, l_ind) # we should just continue, thus return what the next iteration returns

        curr_char = self.input_line[l_ind]
        
        if curr_pattern.pattern == ".":
            res, ind = self.match_recursive(p_ind+1, l_ind+1)
            if res:
                matched = True
                return_ind = max(return_ind, ind)
        elif curr_pattern.pattern_type == CHAR:
            if curr_pattern.pattern == curr_char:
                res, ind = self.match_recursive(p_ind+1, l_ind+1)
                if res:
                    matched = True
                    return_ind = max(return_ind, ind)
        elif curr_pattern.pattern_type == METACHAR:
            if curr_pattern.pattern == r"\w":
                if curr_char in ALPHANUMERIC:
                    res, ind = self.match_recursive(p_ind+1, l_ind+1)
                    if res:
                        matched = True
                        return_ind = max(return_ind, ind)
            elif curr_pattern.pattern == r"\d":
                if curr_char.isnumeric():
                    res, ind = self.match_recursive(p_ind+1, l_ind+1)
                    if res:
                        matched = True
                        return_ind = max(return_ind, ind)
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
                    return_ind = max(return_ind, ind)

        elif curr_pattern.pattern_type == ALTERNATION:
            # in case of backreferrence we have a group too, so the logic is pretty similar
            group_matched = False
            # somehow subpatterns are lists lol!
            for subpattern in curr_pattern.pattern_list:
                curr_l_ind = l_ind
                matched_inds = []

                # unwrap explicitly to be able to backtrack
                if subpattern[-1].pattern == "+":
                    # Try to match as much times as you can
                    while True:
                        try_matcher = Matcher(subpattern[:-1], self.input_line)
                        res, next_ind = try_matcher.match_recursive(l_ind=curr_l_ind)
                        if res and next_ind > curr_l_ind:
                            curr_l_ind = next_ind
                            matched_inds.append(next_ind)
                        else:
                            break

                    # If we have matched continue from the furthest index
                    ref_ind = curr_pattern.group_num
                    for pos in reversed(matched_inds):
                        BACKREFERRENCE_LIST[ref_ind] = parse_all(self.input_line[l_ind:pos])
                        res, end_ind = self.match_recursive(p_ind+1, pos)
                        if res:
                            return (True, end_ind)

                else:
                    test_matcher = Matcher(subpattern,  self.input_line) # treat each option in the group as separate regex to be matched
                    test_res, t_ind = test_matcher.match_recursive(l_ind=l_ind) 
                    
                    if test_res:
                        # continue valid subpattern
                        ref_ind = curr_pattern.group_num
                        BACKREFERRENCE_LIST[ref_ind] = parse_all(self.input_line[l_ind:t_ind])
                        res, ind = self.match_recursive(p_ind+1, l_ind=t_ind)
                        if res:
                            matched = True
                            return_ind = max(return_ind, ind)

        elif curr_pattern.pattern_type == BACKREFERRENCE:
            ref_ind = curr_pattern.pattern
            ref = BACKREFERRENCE_LIST[ref_ind]
            ref_matcher = Matcher(ref + self.pattern[p_ind+1:], self.input_line)
            res, ind = ref_matcher.match_recursive(l_ind=l_ind)
            if res:
                matched = True
                return_ind = max(return_ind, ind)

        elif curr_pattern.pattern == "$":
            if self.input_line[l_ind] == "\0": 
                return (True, l_ind-1) # we should not account the EOF character. Also can just return
            return (False, -1)
        
        if next_pattern and next_pattern.pattern == "+":
            # up to this point we have tried to match one time (and probably have failed)
            # thus we can try to match depending on option provided
            curr_l_ind = l_ind
            matched_inds = []

            # Try to match as much times as you can
            while True:
                try_matcher = Matcher([curr_pattern], self.input_line)
                res, next_ind = try_matcher.match_recursive(l_ind=curr_l_ind)
                if res and next_ind > curr_l_ind:
                    curr_l_ind = next_ind
                    matched_inds.append(next_ind)
                else:
                    break


            # If we have matched continue from the furthest index
            for pos in reversed(matched_inds):
                res, end_ind = self.match_recursive(p_ind+2, pos)
                if res:
                    return (True, end_ind)

            return (False, -1)

        return (matched, return_ind)

# ==================================== functions to build directory tree ============================

class Dir:
    """ Directory tree node"""
    def __init__(self, dirname):
        self.dirname = dirname
        self.files = []
        self.subdirs = []


    def build_dir(self):
        """ Recursively builds directory tree"""
        curr_dir = os.getcwd()

        new_path = os.path.join(curr_dir, self.dirname)
        os.chdir(new_path)
        
        p = Path(".")
        self.files = [str(f) for f in p.iterdir() if f.is_file()]
        subdirs  = [d for d in p.iterdir() if d.is_dir()]

        for subdir_name in subdirs:
            subdir = Dir(subdir_name)
            subdir.build_dir()
            self.subdirs.append(subdir)

        os.chdir("..") # backtrack


    def print_tree(self, tabs=0):
        print(tabs * " ", self.dirname)

        for subdir in self.subdirs:
            subdir.print_tree(tabs+1)


    def name_files(self):
        """ Get path names of each leaf (file) within the tree"""
        files = self.files.copy()

        for subdir in self.subdirs:
            files.extend(subdir.name_files())

        named_files = [str(self.dirname) + "/" + str(file_name) for file_name in files]

        return named_files



# ===================================== matching function for lines/files ==========================


def match_one(pattern_list, input_line):
    """
        Function to match pattern with one line

        args:
            pattern_list: List[RE_Pattern] pattern to match
            input_line: str - input string

        returns:
            matched: bool flag whether pattern has been matched
    """

    input_len = len(input_line)

    if pattern_list[-1].pattern == "$": # add EOF char. Then, we should check the condition "$" == EOF
        input_line += "\0"

    if pattern_list[0].pattern == "^":
        matcher = Matcher(pattern_list[1:], input_line)
        res, ind = matcher.match_recursive()
        if res:
            return True
    else:
        matcher = Matcher(pattern_list, input_line)
        for start_pos in range(input_len):
            res, ind = matcher.match_recursive(l_ind=start_pos)
            if res:
                return True

    return False


def match_file(pattern, file_name, multifile=False):
    """
        Function to match pattern with lines in file

        args:
            pattern: List[RE_Pattern] pattern to match
            file_name: str - to file name
            multifile: bool - if True, prints file name

        returns:
            matched: bool flag whether pattern has been matched with at least one line
    """
    matched = False
    pref = (file_name + ":") if multifile else ""

    with open(file_name) as file:
        for line in file.readlines():
            line = line.rstrip("\n")
            res = match_one(pattern, line)

            if res:
                print(pref + line, file=sys.stdout)
                matched = True

    return matched


def main():
    pattern = sys.argv[2]
    pattern_list = parse_all(pattern)

    if sys.argv[1] not in ["-r", "-E"]:
        print("Expected first argument to be '-E' or '-r'")
        exit(1)

    # simple case with inputing through echo
    if len(sys.argv) == 3:
        input_line = sys.stdin.read()
        res = match_one(pattern_list, input_line)
    else:
        res = False
        # recursively traverse the directory and its subdirectories
        if sys.argv[1] == "-r":
            dir_name = sys.argv[4].rstrip("/")

            pattern = sys.argv[3]
            pattern_list = parse_all(pattern)

            multifile = True
            working_dir = Dir(dir_name) # create dir class
            working_dir.build_dir() # build the tree
            file_name_list = working_dir.name_files() # get all files' names
        # just a multifile query
        else:
            multifile = (len(sys.argv) > 4)
            file_name_list = sys.argv[3:]

        for file_name in file_name_list:
            res |= match_file(pattern_list, file_name, multifile)

    if res:
        exit(0)
    exit(1)

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)


if __name__ == "__main__":
    main()
