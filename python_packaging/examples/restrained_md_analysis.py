import numpy as np
import gmx

# js_tools.py is hypothetical and not included with these examples.
from js_tools import js_calculation, tol


class CalculateJS:
    def __init__(self, params=None, simulation_distances=None):
        """ Do JS-Div calculation """

        self.js = js_calculation(params['DEER'],
                                 simulation_distances)

    def is_converged(self):
        return self.js < tol


calculate_js = gmx.operation.make_operation(
    CalculateJS,
    input=['params', 'simulation_distances'],
    output=['is_converged'])
