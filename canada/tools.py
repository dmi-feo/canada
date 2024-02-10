import slugify as slugify_lib


def slugify(text: str) -> str:
    return slugify_lib.slugify(text, separator="_")
