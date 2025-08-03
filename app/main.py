import sys
import string
import string

# import pyparsing - available if you need it!
# import lark - available if you need it!


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
        elif pattern[pattern_ind] == "\\":
            if pattern[pattern_ind] == input_string[input_ind]:
                return parse(pattern, input_string, pattern_ind+1, input_ind+1)
            return False
        else:
            raise Exception(f"Unknown metacharacter \\{pattern[pattern_ind]}")

    elif pattern[pattern_ind] == "[": # match a group
        # TO DO: invoke parse function after reacing "]". Otherwise it returns None
        # print("GROUP")
        END = pattern.find("]", pattern_ind)
        if len(pattern) >= 2 and pattern[pattern_ind+1] == "^":
            FLAG = True
            pattern_ind += 2

            while pattern_ind != END:
                # create a subpattern
                if pattern[pattern_ind] == "\\":
                    subpattern = f"\\{pattern[pattern_ind+1]}"
                    pattern_ind += 1
                else:
                    subpattern = pattern[pattern_ind]

                # try to match the current subpattern with the current character in the input
                # if at least one match, we should return False
                if parse(subpattern, input_string[input_ind]):
                    FLAG = False
                    break

                pattern_ind += 1 # advance

            if FLAG:
                return parse(pattern, input_string, END+1, input_ind+1)
            return False

        else:
            pattern_ind += 1
            FLAG = False

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


def main():
    pattern = sys.argv[2]
    input_line = sys.stdin.read()


    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)


    input_len = len(input_line)

    if pattern[0] == "^":
        if parse(pattern[1:], input_line):
            exit(0)
        exit(1)


    for start_pos in range(input_len):
        if parse(pattern, input_line, input_ind=start_pos):
            # print(True)
            exit(0)

    exit(1)
    return 
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)


if __name__ == "__main__":
    main()
