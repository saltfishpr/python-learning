from random import randint


def roll(number: int, sides: int) -> int:
    result = 0
    for i in range(number):
        result += randint(1, sides)
    return result
