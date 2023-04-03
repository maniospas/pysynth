from pysynth.data import SourceCodeLine, Variable, Collection, Model
from pysynth.parser.tokenize import *

python_words = {"if", "for", "else"}


def blocks(text: str):
    lines = text.split("\n")
    lines = [line for line in lines]
    lin = [line for line in lines if line.strip()]
    tab = len(lin[0])-len(lin[0].lstrip())
    lines = [line[tab:] for line in lines]
    imports = ""
    block = None
    models = list()
    comment_block = False
    for line in lines:
        if "import " in line:
            imports += line+"\n"
        elif line.strip().startswith("#"):
            if block is not None:
                models.append(imports+block)
            comment_block = True
            block = line
        elif len(line.strip()) == 0:
            if comment_block and block is not None:
                models.append(imports+block)
                block = None
            comment_block = False
        else:
            tab = len(line) - len(line.lstrip())
            if block is None:
                block = line
            elif tab == 0 and not comment_block:
                models.append(imports+block)
                block = line
            else:
                block += "\n"+line
    if block is not None:
        models.append(imports+block)
    return models


def tomodel(text: str):
    lines = text.split("\n")
    lines = [line for line in lines if line.strip()]
    tab = len(lines[0])-len(lines[0].lstrip())
    lines = [line[tab:] for line in lines]

    imports = dict()
    source = list()
    specifications = Collection()
    outputs = list()
    inputs = list()
    last_var = None
    for line in lines:
        line = predicates(line)
        if 'import' in line:
            for symbol in words(line[max(index(line, 'import'), index(line, 'as')) + 1:]):
                imports[symbol] = SourceCodeLine(line)
        else:
            specifications += lemmatize(subwords(words(line)))
            comment_index = index(line, "#")
            if comment_index != -1:
                line = line[:comment_index]
            if not words(line):
                continue
            source.append(SourceCodeLine(line, dependencies=[v for k, v in imports.items() if k in line]))
            eqindex = index(line, "=")
            if eqindex != -1:
                for i in range(eqindex):
                    if (i == 0 or line[i - 1] != ".") and line[i][0] not in special_symbols and line[i] not in imports:
                        if line[i] not in python_words:
                            outputs.append(line[i])
                line = line[eqindex+1:]
            for i in range(len(line)):
                if line[i] == "=":
                    inputs.remove(last_var)
                if (i == 0 or line[i-1] != ".") and line[i][0] not in special_symbols and line[i] not in imports:
                    if line[i] not in python_words:
                        last_var = line[i]
                        inputs.append(last_var)
    inputs = set(inputs)
    outputs = set(outputs)
    return Model(specifications=specifications,
                 expressions=source,
                 inputs=[Variable(varname, lemmatize(subwords([varname]))) for varname in inputs],
                 outputs=[Variable(varname, lemmatize(subwords([varname]))) for varname in outputs])


def code(text: str, dependencies: str = "") -> list[SourceCodeLine]:
    """
    Creates a list of SourceCodeLine objects from the code's and its import dependencies' text.

    :param text: The code text.
    :param dependencies: The dependency text.
    :return: A list of SourceCodeLine objects.
    """
    imports = dict()
    for line in dependencies.split("\n"):
        line = predicates(line.strip())
        if 'import' in line:
            for symbol in words(line[max(index(line, 'import'), index(line, 'as'))+1:]):
                imports[symbol] = SourceCodeLine(line)
    source = list()
    for line in text.split("\n"):
        line = predicates(line)
        source.append(SourceCodeLine(line, dependencies=[v for k, v in imports.items() if k in line]))
    return source


def specs(description: str) -> list[str]:
    """
    Converts text to a list of lemmatized predicates.

    :param description: A string description of the specifications.
    :return: A list of string predicates.
    """
    return Collection(lemmatize(words(predicates(description))))


def var(name: str, description: str, default: str=None) -> Variable:
    """
    Creates a Variable from its name and text description.

    :param name: The variable's name.
    :param description: A text describing the Variable.
    :param default: An optional argument capturing the variable's default value.
    :return: The constructs Variable.
    """
    return Variable(name, specs(description), default=default)
