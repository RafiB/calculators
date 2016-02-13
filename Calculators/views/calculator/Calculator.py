import os
import json

from flask.ext.classy import FlaskView, route

from flask import (
    render_template,
    Response,
)

from Calculators import helpers

from Calculators.models import Calculator


class Index(FlaskView):
    route_base = '/'

    def index(self):
        return render_template('calculator.html')

    @route('/calculator', defaults={'cid': 0})
    @route('/calculator/<int:cid>')
    def calculator_permalink(self, cid):
        calculator = Calculator.query.get(cid)

        if not calculator:
            return Response(json.dumps(
                {
                    'message': "Can't find calculator #{:}".format(
                        cid)
                }
            )), 404

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
