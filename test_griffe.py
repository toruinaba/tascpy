from tascpy.analytics.operations.registry import register_functional

some_op3 = register_functional(lambda x: x, domain="core", name="some_op3")
some_op3.__doc__ = _doc_some_op3 = """This is chained assignment."""
