# pylint: disable=line-too-long

def evaluate(content):
    if 'cookie ' in content:
        return ['Contains "cookie" mention in code. Use "set_variable" or "fetch_variable" instead.']

    return []
