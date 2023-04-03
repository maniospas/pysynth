from pysynth import Database, tomodel, Multispecs, Synthesizer, blocks

database = Database([tomodel(block) for block in blocks(
        """
        import sklearn
        import pickle
        import os
        
        def normalize(x, y):
            x = x / x.sum()  # normalize
            y = y / y.sum()  # normalize
            return x, y
            
        def train_svr(x, y_train):
            x_train = x_train / x_train.sum()  # normalize
            model = sklearn.SVR()
            model.train(x_train, y_train)
            return model
            
        def load_model(path):
            if os.file.exists(path):
                model = pickle.load(path)
            return model
            
        def logistic_regressor():
            model = sklearn.LogisticRegression()
            return model
        
        def standardize(variable):
            # standardize
            variable = variable-variable.mean()
            variable = variable / variable.std()
            
            return variable
        """
    )
])

query = Multispecs(Synthesizer(database))(
    "svr, load it from a path, train the model, normalize training x, standardize y"
)
print(query)
