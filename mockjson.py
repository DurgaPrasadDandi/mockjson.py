#!/usr/bin/env python

"""mockjson.py: Library for mocking JSON objects from a template."""

__author__ = "James McMahon"
__copyright__ = "Copyright 2012, James McMahon"
__license__ = "MIT"

try:
    import simplejson as json
except ImportError:
    import json
import random
import re
import string
import sys

from datetime import datetime, timedelta

_male_first_name = """James John Robert Michael William David
    Richard Charles Joseph Thomas Christopher Daniel
    Paul Mark Donald George Kenneth Steven Edward
    Brian Ronald Anthony Kevin Jason Matthew Gary
    Timothy Jose Larry Jeffrey Frank Scott Eric""".split()
_female_first_name = """Mary Patricia Linda Barbara Elizabeth
    Jennifer Maria Susan Margaret Dorothy Lisa Nancy
    Karen Betty Helen Sandra Donna Carol Ruth Sharon
    Michelle Laura Sarah Kimberly Deborah Jessica
    Shirley Cynthia Angela Melissa Brenda Amy Anna""".split()
_last_name = """Smith Johnson Williams Brown Jones Miller
    Davis Garcia Rodriguez Wilson Martinez Anderson
    Taylor Thomas Hernandez Moore Martin Jackson
    Thompson White Lopez Lee Gonzalez Harris Clark
    Lewis Robinson Walker Perez Hall Young Allen""".split()
_lorem = """lorem ipsum dolor sit amet consectetur adipisicing elit
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua
    Ut enim ad minim veniam quis nostrud exercitation ullamco laboris
    nisi ut aliquip ex ea commodo consequat Duis aute irure dolor in
    reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
    pariatur Excepteur sint occaecat cupidatat non proident sunt in
    culpa qui officia deserunt mollit anim id est laborum""".split()


def _random_data(key):
    if not key in data:
        return key
    return data[key]()


def _lorem_ipsum():
    length = random.randrange(2, len(_lorem) / 2)
    return ' '.join(random.choice(_lorem) for _ in xrange(length))


def _random_date():
    return datetime.today() - timedelta(days=random.randrange(6571, 27375))

# assigning regexes to variables removes regex cache lookup overhead
_re_range = re.compile(r"\w+\|(\d+)-(\d+)")
_re_strip_key = re.compile(r"\|(\d+-\d+|\+\d+)")
_re_increments = re.compile(r"\w+\|\+(\d+)")
_re_key = re.compile(r"(@[A-Z_0-9\(\),]+)")

data = dict(
    NUMBER=lambda: random.choice(string.digits),
    LETTER_UPPER=lambda: random.choice(string.uppercase),
    LETTER_LOWER=lambda: random.choice(string.lowercase),
    MALE_FIRST_NAME=lambda: random.choice(_male_first_name),
    FEMALE_FIRST_NAME=lambda: random.choice(_female_first_name),
    LAST_NAME=lambda: random.choice(_last_name),
    EMAIL=lambda: (_random_data('LETTER_LOWER')
                      + '.'
                      + _random_data('LAST_NAME').lower()
                      + '@'
                      + _random_data('LAST_NAME').lower()
                      + '.com'),
    LOREM=lambda: random.choice(_lorem),
    LOREM_IPSUM=_lorem_ipsum,
    DATE_YYYY=lambda: str(_random_date().year),
    DATE_MM=lambda: str(_random_date().month).zfill(2),
    DATE_DD=lambda: str(_random_date().day).zfill(2),
    TIME_HH=lambda: str(_random_date().hour).zfill(2),
    TIME_MM=lambda: str(_random_date().minute).zfill(2),
    TIME_SS=lambda: str(_random_date().second).zfill(2)
)


def mock_object(template, increments={}, name=None):
    length = 0
    if name:
        matches = _re_range.search(name)
        if matches:
            groups = matches.groups()
            length_min = int(groups[0])
            length_max = int(groups[1])
            length = random.randint(length_min, length_max)

    t_type = type(template)
    if t_type is dict:
        generated = {}
        for key, value in template.iteritems():
            # handle increments
            inc_matches = _re_increments.search(key)
            if inc_matches and type(template[key]) is int:
                increment = int(inc_matches.groups()[0])
                if key in increments:
                    increments[key] += increment
                else:
                    increments[key] = 0

            stripped_key = _re_strip_key.sub('', key)
            generated[stripped_key] = mock_object(value, increments, key)
        return generated
    elif t_type is list:
        return [mock_object(template[0], increments) for _ in xrange(length)]
    elif t_type is int:
        if name in increments:
            return increments[name]
        else:
            return length if matches else template
    elif t_type is bool:
        # apparently getrandbits(1) is faster...
        return random.choice([True, False]) if matches else template
    # is this always just going to be unicode here?
    elif t_type is str or t_type is unicode:
        if template:
            length = length if length else 1
            generated = ''.join(template for _ in xrange(length))
            matches = _re_key.findall(generated)
            if matches:
                for key in matches:
                    rd = _random_data(key.lstrip('@'))
                    generated = generated.replace(key, rd, 1)
            return generated
        else:
            return (''.join(random.choice(string.letters)
                         for i in xrange(length)))
    else:
        return template


def mock_json(template):
    return json.dumps(mock_object(json_data), sort_keys=True, indent=4)


if __name__ == '__main__':
    arg = sys.argv[1:][0]
    with open(arg) as f:
        json_data = json.load(f)
    print(mock_json(json_data))
