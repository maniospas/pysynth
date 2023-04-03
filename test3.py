from pysynth import Database, tomodel, Multispecs, Synthesizer, blocks, load

database = Database([tomodel(block) for block in blocks(load("examples.py"))])
query = "svr, load it from a path, train the model, normalize training x, standardize y"
result = Multispecs(Synthesizer(database))(query)
print(result)
