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

    formula = None
    with open(formula_descr) as f:
        formula = f.read()

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


def write_template_file(template, formula=None):
    template = os.path.join(app.root_path, 'templates', 'formulae',
                            template)

    with open(template, 'w') as f:
        if formula is None:
            formula = '''{% extends 'calculator.html' %}

{%-
set labels = {
}
-%}

{%- block formula -%}
{{ labels if get_labels else 'formula' }}
{%- endblock -%}'''

        f.write(formula)


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
    return instance
