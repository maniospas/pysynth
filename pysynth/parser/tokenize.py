special_symbols = {c for c in ".,!@#$%^/&*()-+={}[]:\t=<>`'\"\n "}
stopwords = {"a", "to", "from", "it", "the"}


def predicates(text: str) -> list[str]:
    predicate = None
    is_special = False
    preds= list()
    for pos, c in enumerate(text):
        next_is_special = c in special_symbols
        if predicate is None:
            is_special = next_is_special
            predicate = str(c)
            continue
        if c == '\n' or c == '\t' or c == ' ' or c == '.' or c == '(' or c == ')' or c == '#' or (c == '=' and (pos == len(text)-1 or text[pos+1] != "=") and (predicate is None or predicate[-1] not in ["=", ">", "<"])):
            if predicate is not None:
                preds.append(predicate)
            preds.append(str(c))
            predicate = None
            continue
        if is_special == next_is_special:
            predicate += c
        else:
            preds.append(predicate)
            predicate = str(c)
            is_special = next_is_special
    if predicate is not None:
        preds.append(predicate)
    return preds


def index(preds: list[str], query) -> int:
    depth = 0
    for i, pred in enumerate(preds):
        if pred == "]" or pred == ")" or pred == "}":
            depth -= 1
        if pred == query and depth == 0:
            return i
        if pred == "[" or pred == "(" or pred == "{":
            depth += 1
    return -1


def stem(preds: list[str]) -> list[str]:
    from nltk.stem import PorterStemmer
    stemmer = PorterStemmer()
    return [stemmer.stem(pred) for pred in preds if pred not in stopwords]


def words(preds: list[str]) -> list[str]:
    return [pred for pred in preds if pred[0] not in special_symbols]


def _camel_case_split(text):
    # source: https://www.geeksforgeeks.org/python-split-camelcase-string-to-individual-strings/
    if not text:
        return text
    words = [[text[0]]]
    for c in text[1:]:
        if words[-1][-1].islower() and c.isupper():
            words.append(list(c))
        else:
            words[-1].append(c)
    return [''.join(word) for word in words]


def subwords(preds: list[str]) -> list[str]:
    preds = words(preds)
    return [subword.lower() for word in preds for interword in word.split("_") for subword in _camel_case_split(interword)]
