# pylint: disable=line-too-long

def evaluate(content):
    if 'print ' in content or 'print(' in content:
        return ['Contains "print" statement or function call. This may be unsafe in Unicode contexts.']

    return []
