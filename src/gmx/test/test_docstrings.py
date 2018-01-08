"""Test embedded documentaion-by-example in docstrings.

It is probably sufficient to just do this from a sphinx-build doctest.
"""
#
# import doctest
# import gmx

# Note pytest does not support load_tests protocol as of Pytest 3.2.0 and is unlikely to any time soon
# def load_tests(loader, tests, ignore):
#     #tests.addTests(doctest.DocTestSuite(gmx))
#     tests.addTests(doctest.DocTestSuite(gmx.exceptions))
#     #tests.addTests(doctest.DocTestSuite(gmx.fileio))
#     #tests.addTests(doctest.DocTestSuite(gmx.util))
#     return tests
#
# if __name__ == '__main__':
#     unittest.discover()