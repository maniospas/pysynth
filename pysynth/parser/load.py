def load(path: str) -> str:
    text = ""
    with open(path) as file:
        for line in file:
            text += line
    return text