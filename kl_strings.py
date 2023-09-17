def clear_string(s):
    chars_to_remove = ('"', ' ', '\r', '\n', "'", ',', '.')
    while len(s) != 0 and s[0] in chars_to_remove:
        s = s[1:]
    while len(s) != 0 and s[-1] in chars_to_remove:
        s = s[:-1]
    return s