from pysynth import Database, tomodel, Multispecs, Synthesizer, blocks, load

models = [tomodel(block) for block in blocks(load("examples.py"))]
print(models[0])
database = Database(models)
query = "svr, load it from a path, train the model from x y, normalize training x, standardize y"
result = Multispecs(Synthesizer(database))(query)
print(result)
