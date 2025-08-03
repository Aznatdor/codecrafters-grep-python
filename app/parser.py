import string

ALPHANUMERIC = set("_" + string.ascii_letters + string.digits)


def parse(pattern, input_string, pattern_ind=0, input_ind=0):
    # print(pattern, input_string, pattern_ind, input_ind)
    # print("PATTERN LEN", len(pattern))
    if pattern_ind >= len(pattern):
        # print("HERE")
        return True
    if input_ind >= len(input_string): return False

    if pattern[pattern_ind] == "\\": # metacharacter
        # print("METACHAR")
        pattern_ind += 1

        if pattern[pattern_ind] == "d": # match with one digit
            if input_string[input_ind].isnumeric():
                return parse(pattern, input_string, pattern_ind+1, input_ind+1)
            return False

        elif pattern[pattern_ind] == "w": # match with one alphanumeric character
            if input_string[input_ind] in ALPHANUMERIC:
                return parse(pattern, input_string, pattern_ind+1, input_ind+1)
            return False
        else:
            raise Exception(f"Unknown metacharacter \\{pattern[pattern_ind]}")

    elif pattern[pattern_ind] == "[": # match a group
        # TO DO: invoke parse function after reacing "]". Otherwise it returns None
        # print("GROUP")
        FLAG = True
        END = pattern.find("]", pattern_ind)
        if len(pattern) >= 2 and pattern[pattern_ind+1] == "^":
            pattern_ind += 2

            while pattern_ind != END:
                # create a subpattern
                if pattern[pattern_ind] == "\\":
                    subpattern = f"\\{pattern[pattern_ind+1]}"
                    pattern_ind += 1
                else:
                    subpattern = pattern[pattern_ind]

                # try to match the current subpattern with the current character in the input
                print(subpattern, input_string[input_ind])
                # if at least 1 match, return False
                if parse(subpattern, input_string[input_ind]):
                    FLAG = False
                    break

                pattern_ind += 1 # advance

            if FLAG:
                return parse(pattern, input_string, END+1, input_ind+1)
            return False

        else:
            pattern_ind += 1

            while pattern_ind != END:
                if pattern[pattern_ind] == "\\":
                    subpattern = f"\\{pattern[pattern_ind+1]}"
                    pattern_ind += 1
                else:
                    subpattern = pattern[pattern_ind]
                if parse(subpattern, input_string[input_ind]):
                    FLAG = True
                    break

                pattern_ind += 1 # advance
            if FLAG:
                return parse(pattern, input_string, END+1, input_ind+1)
            return False

    else: # match one character
        # print("CHAR")
        if pattern[pattern_ind] == input_string[input_ind]:
            return parse(pattern, input_string, pattern_ind+1, input_ind+1)
        return False


if __name__ == "__main__":
    print(parse(r"[^ban]", "b"))
    print(parse(r"[^ban]", "a"))
    print(parse(r"[^ban]", "n"))
    print(parse(r"[^ban]", "i"))
