from pysynth import Database, tomodel, Multispecs, Synthesizer, blocks

database = Database([tomodel(block) for block in blocks(
        """
        import sklearn
        import pickle
        import os
        model = sklearn.SVR()
        model = sklearn.LogisticRegression()
        model = sklearn.LogisticRegression(seeds=seed)
        model.train(x, y)
        if os.file.exists(path):
            model = pickle.load(path)
        
        # standardize
        variable = variable-variable.min()
        variable = variable / variable.max()
        
        variable = variable/variable.sum()  # normalize
        """
    )
])

query = Multispecs(Synthesizer(database))(
    "svr with seed, load it from a path, train it, normalize variable x, standardize y"
)
print(query)
