import os

from Calculators import helpers

from flask.ext.classy import FlaskView, route

from flask import (
    render_template,
    Response,
)


def get_calculator(calc_name):
    # TODO get c from a database instead
    c = Calculator()
    c.name = 'Compound Interest'
    c.template = calc_name + '.formula'
    if calc_name == 'BMI':
        c.name = 'Body Mass Index'
    return c


class Calculator(object):
    name = None
    template = None


class Index(FlaskView):
    route_base = '/'

    @route('/', defaults={'calc_name': 'compound_interest'})
    @route('/<calc_name>/')
    def index(self, calc_name):
        template_name = get_calculator(calc_name).template
        template = os.path.join('formulae', template_name)

        variables, success = helpers.get_template_variables(template)

        if not success:
            # TODO handle this nicely
            return Response("Didn't find calculator {:}".format(
                template_name)), 404

        return render_template(template,
                               calculator_name=template_name,
                               variables=list(variables))
