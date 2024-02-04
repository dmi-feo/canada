import random
import string

import transliterate
import slugify as slugify_lib


def get_random_string(length):
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    # print random string
    return result_str


def slugify(text: str) -> str:
    return slugify_lib.slugify(text, separator="_")  # TODO: separator="_"
