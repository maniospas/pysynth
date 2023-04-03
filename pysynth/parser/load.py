from pysynth.parser.tokenize import predicates
from pysynth.data import Model, SourceCodeLine, Variable
from pysynth.parser.tokenize import special_symbols


def sublist(preds: list[str], first: str = None, last: str = None):
    started = True if first is None else False
    ret = list()
    for pred in preds:
        if not started and first is not None and pred == first:
            started = True
        elif started and last is not None and pred == last:
            break
        elif started:
            ret.append(pred)
    return ret


def words(preds: list[str]):
    return [pred for pred in preds if pred[0] not in special_symbols]


def strip(preds: list[str]):
    if not preds:
        return preds
    i = 0
    while i < len(preds)-1 and preds[i] == ' ' or preds[i] == '\t':
        i += 1
    return preds[i:]



stopwords = {"def", "return"}
def remove_stopwords(preds):
    return [word for word in preds if word not in stopwords and len(word) > 1]


def index(preds: list[str], query):
    for i, pred in enumerate(preds):
        if pred == query:
            return i
    return -1


def _load_lines(path: str):
    text = ""
    with open(path) as file:
        for line in file:
            text += line

    lines = list()
    line = list()

    for predicate in predicates(text):
        if '#' in predicate:
            lines.append(line)
            line = list()
        if predicate == '\n':
            lines.append(line)
            line = list()
        else:
            line.append(predicate)
    if line:
        lines.append(line)

    return lines


def load(path: str):
    lines = _load_lines(path)
    imports = dict()
    inputs = None
    outputs = None
    models = list()
    function_specs = list()
    prev_line_specs = None
    for line in lines:
        if 'import' in line:
            for symbol in words(line[max(index(line, 'import'), index(line, 'as'))+1:]):
                imports[symbol] = SourceCodeLine(strip(line))
        elif 'def' in line:
            function_specs = list()#subwords(line)
            if '#' in line:
                line = line[:index(line, '#')]
            outputs = dict()
            inputs = dict()
            for var in words(sublist(line, '(', ')')):
                inputs[var] = Variable(var, specifications=subwords([var]))
        elif strip(line) and strip(line)[0] == '#':
            function_specs = subwords(line)
        elif inputs is not None and outputs is not None:
            line_specs = function_specs + subwords(line)
            prev_line_specs = line_specs
            if '#' in line:
                line = line[:index(line, '#')]
            if len(line) < 3:
                continue
            if '=' in line:
                for var in words(sublist(line, last='=')):
                    variable = Variable(var, specifications=subwords([var]))
                    inputs[var] = variable
                    outputs[var] = variable
            linewords = words(line)
            for var in list(inputs.values()) + list(outputs.values()):
                i = index(linewords, var.name)
                if i != -1 and i > 0:
                    var.specifications.extend(["before "+word for word in subwords(linewords[:i])]+subwords(linewords[:i]))
                if i != -1 and i < len(linewords)-1:
                    var.specifications.extend(["before "+word for word in subwords(linewords[i+1:])]+subwords(linewords[i+1:]))
            models.append(Model(line_specs,
                                [SourceCodeLine(strip(line), dependencies=[imports[dependency] for dependency in imports if dependency in line])],
                                [variable for var, variable in inputs.items() if var in line],
                                [variable for var, variable in outputs.items() if var in line],
                            ))
    for model in models:
        print("------------")
        print(model)
    #else:
    #    if 'def' not in line and '#' not in ''.join(line):
    return models
