import sys
import string

# import pyparsing - available if you need it!
# import lark - available if you need it!


ALPHANUMERIC = set(string.ascii_letters + string.digits + "_")


def match_pattern(input_line, pattern):
    if len(pattern) == 1:
        return pattern in input_line
    elif pattern == r"\d":
        return any(char.isdigit() for char in input_line)
    elif pattern == r"\w":
        return any(char in ALPHANUMERIC for char in input_line)
    elif pattern.startswith("[^"):
        char_group = pattern[2:-1]
        return any(char not in char_group for char in input_line)
    elif pattern[0] == "[":
        char_group = pattern[1:-1]
        return any(char in char_group for char in input_line)
    else:
        raise RuntimeError(f"Unhandled pattern: {pattern}")


def main():
    pattern = sys.argv[2]
    input_line = sys.stdin.read()

    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # Uncomment this block to pass the first stage
    if match_pattern(input_line, pattern):
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
