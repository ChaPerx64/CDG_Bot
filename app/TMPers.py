# Returns text in UTF-8 from messages stored subfolder "custom_messages"

import os
from os.path import dirname, join


def rf_text(f_name: str):
    try:
        with open(f_name, encoding='utf-8') as t:
            return t.read()
    except FileNotFoundError:
        return 'Доброе утро 🌞'


def wf_text(f_name: str, text: str):
    with open(f_name, 'w', encoding='utf-8') as t:
        t.write(text)
        return True
