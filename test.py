from pysynth import Model, SourceCodeLine, Database, Greedy, predicates, code, var, specs

pygrankimport = SourceCodeLine(predicates("import pygrank as pg"))

database = Database([
    Model(
        specifications=specs("run personalized pagerank filter"),
        expressions=code("r = pg.Pagerank(0.85)(p)", "import pygrank as pg"),
        inputs=[var("p", "pagerank personalization")],
        outputs=[var("r", "pagerank ranks")]
    ),
    Model(
        specifications=specs("create personalization for filter"),
        expressions=code("p2 = pg.tosignal(G, nodes)", "import pygrank as pg"),
        inputs=[var("nodes", "a set of nodes"), var("G", "a graph")],
        outputs=[var("p2", "pagerank personalization")]
    )
])

query = Model(specs("personalized pagerank filter create personalization"), [], [], [])

query = Greedy(database)(query)
print(query)
