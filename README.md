# pysynth
Implements linear program synthesis in python.

## :compass: Progrss
- [x] Behaviorizeable relations
- [x] Linear code synthesis
- [ ] Database management
- [ ] Web service

## :rocket: Quickstart
*This is a tentative programming interface*

You can parse a file containing import statements
and method definitions with the following snippet:

```python
from pysynth import tomodel, blocks, load

models = [tomodel(block) for block in blocks(load("examples.py"))]
```

This creates a list of models, each of which contains a list
of specification predicates describing them (basically keywords
extracted from some source code), source code expressions,
and indication of input and output variables, depending on which
variables are assigned values and which are used in the code.
This is an example of the information a model holds:

```python
print(models[0])

# Specifications: x x x sum normal
# Inputs: [x]
# Outputs: [x]
x = x / x.sum()  
```

The following code pack these models into a database that splits the 
specification and the implementation and variable part
and maps this correspondence. It then defines a synthesis mechanism
tha runs on this database. Synthesizer performs linear replacement
of one set of specifications with its implementation. Multispecs
repeats this process for multiple comma-separated specification texts.

```python
from pysynth import Database, Multispecs, Synthesizer

database = Database(models)
synthesize = Multispecs(Synthesizer(database))
```

To synthesize code, run the synthesis mechanism with a string query
(use commas to separate multiple steps):

```python
query = "svr, load it from a path, train the model, normalize training x, standardize y"
result = synthesize(query)
print(result)

# Specifications: y
# Inputs: [model,path,return,x_train,y_train]
# Outputs: [model,x_train,y_train]
import pickle
import sklearn
import os
model = sklearn.SVR()
if os.path.exists(path):
    model = pickle.load(path)
    return model
x_train = x_train / x_train.sum()  
y_train = y_train - y_train.mean()
y_train = y_train / y_train.std()
model.train(x_train, y_train)

```