import os
import ast
import json

from Calculators import helpers
from Calculators.models import Calculator, Tag

from flask import (
    redirect,
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

    @route('/calculate', methods=['POST'])
    def calculate(self):
        if 'calculator' not in request.form or \
                not Calculator.query.filter_by(
                    template=request.form['calculator']):
            return Response(json.dumps(
                {
                    'message': "Dict not okay. You must supply a valid "
                               "calculator in the POST request."
                }
            )), 404

        template_name = request.form['calculator']
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
        labels['calculator'] = (calculator.template,)

        return 'You need to supply {:} in the post request to {:}'.format(
            {k: v[0] for k, v in labels.iteritems()},
            url_for('Endpoint:calculate', _external=True)
        )

    @route('/seach_by_tags/<search_string>')
    def search_by_tags(self, search_string):
        search_string = search_string.lower()
        search_tags = search_string.split()

        cs = Calculator.query.filter(
            Calculator.tags.any(
                or_(*[func.lower(Tag.name).like('%'+t+'%')
                      for t in search_tags])
            )
        ).all()

        calculators = [
            {
                'name': c.name,
                'tags': list(set([t.name for t in c.tags for tag in search_tags
                                  if tag in t.name.lower()])),
                'id': c.id
            }
            for c in cs]

        calculators = sorted(
            calculators,
            key=lambda x: (search_string in x['name'].lower(), len(x['tags'])),
            reverse=True)

        return json.dumps(calculators)

    @route('/get_html_form_by_id', methods=['POST'])
    def get_html_form_by_id(self):
        # TODO is it better to return rendered HTML, or a JSON dict for the JS
        # to create the form?

        got_id = Schema({'id': Coerce(int)}, required=True, extra=True)

        try:
            okay_form = got_id(request.form)
        except MultipleInvalid:
            return Response(json.dumps(
                {
                    'message': 'You must include a calculator id in the POST '
                    'data.'
                }
            )), 400

        return redirect(url_for('Index:calculator_permalink_0',
                                cid=okay_form['id']))
