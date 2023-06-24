import logging
import sys

from flow import Flow


def is_integer(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


flow = Flow[str]()

valid, invalid = flow. \
    map(lambda s: s.strip()). \
    filter(lambda s: s != ""). \
    segregate(is_integer, True, False)

# invalid strings
invalid.peep(lambda s: logging.error("Invalid integer '%s'", s))

# valid strings
integers = valid. \
    map(int). \
    peep(lambda i: print(f"insert into table(n) values({i});")) \
    .collect()

flow.send(sys.stdin)
print(integers)
