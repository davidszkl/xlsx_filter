from shlex import split as ssplit
import operator

OPERATORS = {
    '<': operator.lt,
    '<=': operator.le,
    '>': operator.gt,
    '>=': operator.ge,
    '==': operator.eq,
    '!=': operator.ne,
}

def parse_domain(domain: str):
    elements = ssplit(domain)
    if not len(elements) == 3:
        return None
    try:
        elements[2] = float(elements[2])
    except ValueError:
        elements[2] = str(elements[2].strip("'"))
    return (
        elements[0],
        OPERATORS[elements[1]],
        elements[2],
    )
