import re
import json
from ast import literal_eval

"""
OpenAlex incluye los abstracts de los trabajos, pero están guardados
como índices invertidos, por un tema legal. Para poder convertirlos a texto
común y corriente, se puede utilizar esta funnción.
"""


def abstract_to_plain_text(inverted_abstract):
    list_length = 0

    for val in inverted_abstract.values():
        for digit in val:
            if digit > list_length:
                list_length = digit

    abstract_list = [""] * (list_length + 1)

    for key, val in inverted_abstract.items():
        for digit in val:
            abstract_list[digit] = key

    return " ".join(abstract_list)
