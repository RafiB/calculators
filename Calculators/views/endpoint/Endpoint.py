import os
import ast
import json

from Calculators import helpers
from Calculators.models import Calculator, Tag

from flask import (
    render_template,
    Response,
    request,
    url_for,
)

from flask.ext.classy import FlaskView, route

from sqlalchemy import func, or_

from voluptuous import Coerce, Schema, MultipleInvalid


class Endpoint(FlaskView):
    route_base = '/rest/api/current/'

    def index(self):
        return 'TODO: serve some data'

    @route('/calculate', methods=['POST'])
    def calculate(self):
        if 'calculator' not in request.form:
            return Response(json.dumps(
                {
                    'message': "Dict not okay. You must supply a valid "
                               "calculator in the POST request."
                }
            )), 404

        template_name = request.form.get('calculator')
        template = os.path.join('formulae', template_name)

        variables, success = helpers.get_template_variables(template)

        if not success:
            return Response(json.dumps(
                {
                    'message': "Can't find calculator {:}".format(
                        template_name)
                }
            )), 404

        # Check that all variables are present in the POST'd form
        form_schema = Schema(
            {v: Coerce(float) for v in variables},
            required=True,
            extra=True
        )

        supplied = set([k for k, v in request.form.iteritems() if v])

        try:
            formula_vars = form_schema(request.form)
        except MultipleInvalid:
            missing = list(variables - supplied)
            return Response(json.dumps(
                {
                    'missing': missing
                }
            )), 400

        # Evaluate the formula with the variables!
        return render_template(template, **formula_vars)

    @route('/calculator/<calculator>/variables')
    def get_calculator_variables(self, calculator):
        template = os.path.join('formulae', calculator+'.formula')

        variables, success = helpers.get_template_variables(template)

        if not success:
            return Response("Can't find calculator {:}".format(
                calculator)), 404

        # TODO is there a way to get `labels` straight out of the template?
        labels = ast.literal_eval(render_template(template, get_labels=True))
        labels['calculator'] = (calculator+'.formula',)

        return 'You need to supply {:} in the post request to {:}'.format(
            {k: v[0] for k, v in labels.iteritems()},
            url_for('Endpoint:calculate', _external=True)
        )

    @route('/seach_by_tags/<search_string>')
    def search_by_tags(self, search_string):
        calculators = []

        search_string = search_string.lower()

        cs = Calculator.query.filter(
            Calculator.tags.any(
                or_(*[func.lower(Tag.name).like('%'+t+'%')
                      for t in search_string.split()])
            )
        ).all()
        calculators += [c.name for c in cs]

        return json.dumps(calculators)

    @route('/get_html_form_by_name', methods=['POST'])
    def get_html_form_by_name(self):
        # TODO is it better to return rendered HTML, or a JSON dict for the JS
        # to create the form?

        if 'name' not in request.form:
            return Response(json.dumps(
                {
                    'message': 'You must include a calculator name in the POST '
                    'data.'
                }
            )), 400

        calculator = Calculator.query.filter_by(name=request.form['name']).first()
        if not calculator:
            return Response(json.dumps(
                {
                    'message': "That calculator doesn't exist!"
                }
            )), 400


        template_name = calculator.template
        template = os.path.join('formulae', template_name)

        variables, success = helpers.get_template_variables(template)

        if not success:
            return Response(json.dumps(
                {
                    'message': "Can't find calculator {:}".format(
                        template_name)
                }
            )), 404

        return render_template(template,
                                calculator_name=template_name,
                                variables=list(variables))
