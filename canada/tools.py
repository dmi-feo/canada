import random
import string

import transliterate


def get_random_string(length):
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    # print random string
    return result_str


def simplify_string(title: str) -> str:
    return transliterate.slugify(title)
