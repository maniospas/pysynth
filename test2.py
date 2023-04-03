from pysynth import Model, SourceCodeLine, Database, Synthesizer, predicates, code, var, specs, Multispecs


database = Database([
    Model(
        specifications=specs("create an svr model"),
        expressions=code("svr = sklearn.SVR()", "import sklearn"),
        inputs=[],
        outputs=[var("svr", "model")]
    ),
    Model(
        specifications=specs("create a logistic regression model"),
        expressions=code("lr = sklearn.LogisticRegression()", "import sklearn"),
        inputs=[],
        outputs=[var("lr", "model")]
    ),
    Model(
        specifications=specs("create a logistic regression model with seeded state"),
        expressions=code("lr = sklearn.LogisticRegression(random_state=seed)", "import sklearn"),
        inputs=[var("seed", "random state", default="0")],
        outputs=[var("lr", "model")]
    ),
    Model(
        specifications=specs("load a model from path"),
        expressions=code("if os.path.exists(path):\n   custom = pickle.load(path)", "import pickle\nimport os"),
        inputs=[var("path", "path")],
        outputs=[var("custom", "model")]
    ),
    Model(
        specifications=specs("train a model"),
        expressions=code("model.train(x, y)"),
        inputs=[var("model", "model"), var("x", "training input variable"), var("y", "training output variable")],
        outputs=[]
    ),
    Model(
        specifications=specs("train a model with weights"),
        expressions=code("model.train(x, y, weights=weights)"),
        inputs=[var("model", "model"), var("x", "training input variable"), var("y", "training output variable"),
                var("weights", "training weights")],
        outputs=[]
    ),
    Model(
        specifications=specs("save a model"),
        expressions=code("pickle.dump(path, model2)", "import pickle"),
        inputs=[var("model2", "model"), var("path", "path")],
        outputs=[]
    ),
    Model(
        specifications=specs("normalize"),
        expressions=code("xn = xn/xn.sum()"),
        inputs=[var("xn", "variable")],
        outputs=[var("xn", "variable")]
    ),
])


query = Multispecs(Synthesizer(database))(
    "create a logistic regression model, load it, normalize inputs, normalize outputs, save model"
)
print(query)
