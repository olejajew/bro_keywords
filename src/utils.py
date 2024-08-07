import re


def extract_digits(input_string):
    return ''.join(re.findall(r'\d', input_string))