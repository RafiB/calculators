import os

from Calculators import app

from jinja2 import Environment, meta


def get_template_variables(template):
    '''
        Get the variables from a template file.

        Returns the variables, and a boolean expressing success / failure
    '''

    formula_descr = os.path.join(app.root_path, 'templates', template)
    if not os.path.isfile(formula_descr):
        return [], False

    formula = open(formula_descr).read()

    variables = meta.find_undeclared_variables(Environment().parse(formula))
    if 'labels' in variables:
        variables.remove('labels')
    if 'get_labels' in variables:
        variables.remove('get_labels')

    return variables, True
