import os

from Calculators import helpers

from flask import (
    render_template,
    Response,
    request,
)

from flask.ext.classy import FlaskView, route

from voluptuous import Coerce, Schema, MultipleInvalid


class Endpoint(FlaskView):
    route_base = '/rest/api/current/'

    def index(self):
        return 'TODO: serve some data'

    @route('/calculate', methods=['POST'])
    def calculate(self):
        if 'calculator' not in request.form:
            r = 'Dict not okay. You must supply a valid calculator ' \
                'in the POST request.'
            return Response(r), 400

        template_name = request.form.get('calculator')
        template = os.path.join('formulae', template_name)

        variables, success = helpers.get_template_variables(template)

        if not success:
            # TODO handle this nicely
            return Response("Didn't find calculator {:}".format(
                template_name)), 404

        # Check that all variables are present in the POST'd form
        form_schema = Schema(
            {v: Coerce(float) for v in variables},
            required=True,
            extra=True
        )

        try:
            formula_vars = form_schema(request.form)
        except MultipleInvalid:
            r = 'Dict not okay. You must supply {:} as integer or decimal ' \
                   'args in the POST request'.format(', '.join(list(variables)))
            return Response(r), 400

        # Evaluate the formula with the variables!
        return render_template(template, **formula_vars)
