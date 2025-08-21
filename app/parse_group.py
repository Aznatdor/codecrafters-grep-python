# Algorithm for parsing groups

def parse_group(pattern):
    """
        args:
            pattern: str - some string with groups (arbitrary depth) encosed by "(", ")" and splitted with "|"
                           without loss of generality pattern should begin with ( and end with )
            
        returns:
            groups: list - list, where each element is group
    """

    stack = [[]]
    curr = ""

    for char in pattern:
        if char == "(":
            stack.append([])
        elif char == ")":
            if curr:
                stack[-1].append(curr)
            curr = ""
            tmp = stack.pop()
            stack[-1].append(tmp)
        elif char == "|":
            if curr:
                stack[-1].append(curr)
            curr = ""
        else:
            curr += char

    if len(stack) > 1:
        raise(ValueError("Unmatched parentheses"))

    return stack[0]


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


if __name__ == "__main__":
    #pattern = "((abc|bca)|a|b|((a|b)|(b|c)))"
    #pattern = "(abc)"
    pattern = "((abc)(abc))"
    print(pattern)
    res = split_group(pattern)
    print(res)
