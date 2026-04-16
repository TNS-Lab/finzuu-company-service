import math, random

def generate_reference(key_length: int):
    key = ""
    key_element = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    length = len(key_element)
    for i in range(key_length):
        key += key_element[math.floor(random.random() * length)]

    return key


def generate_key(key_length: int):
    key = ""
    key_element = "_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_@$%&/"

    length = len(key_element)
    for i in range(key_length):
        key += key_element[math.floor(random.random() * length)]

    return key
