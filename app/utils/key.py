import math, random
import string

def generate_reference(key_length: int):
    key = ""
    key_element = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    length = len(key_element)
    for i in range(key_length):
        key += key_element[math.floor(random.random() * length)]

    return key


def generate_key(key_length: int):
    min_length = max(key_length, 8)
    required_chars = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("_@$%&/"),
    ]
    key_element = "_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_@$%&/"
    remaining_chars = [random.choice(key_element) for _ in range(min_length - len(required_chars))]
    key_chars = required_chars + remaining_chars
    random.shuffle(key_chars)

    return "".join(key_chars)
