import sys

# import pyparsing - available if you need it!
# import lark - available if you need it!

def match_digit(input_line, pattern):
    if r"\d" ==  pattern:
        return any(map(lambda x: x.isnumeric(), input_line))

def match_pattern(input_line, pattern):
    if len(pattern) == 1:
        return pattern in input_line
    if len(pattern) == 2:
        res = match_digit(input_line, pattern)
        if res:
            print("Matched!", file=sys.stderr)
        return res
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
