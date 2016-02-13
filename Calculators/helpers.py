import os

from Calculators import app

from jinja2 import Environment, meta

from Calculators.models import Calculator


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

    return list(variables), True


def get_template_variables_by_id(id):
    calculator = Calculator.query.get(id)

    if not calculator:
        return False, "Can't find calculator #{:}".format(id)

    template_name = calculator.template
    template = os.path.join('formulae', template_name)

    result, success = get_template_variables(template)

    if not success:
        result = "There's no calculator with id {:}".format(id)
    else:
        result = (template, template_name, result)

    return success, result
