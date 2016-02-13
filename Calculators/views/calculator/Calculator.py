import json

from flask.ext.classy import FlaskView, route

from flask import (
    render_template,
    Response,
)

from Calculators import helpers


class Index(FlaskView):
    route_base = '/'

    def index(self):
        return render_template('calculator.html')

    @route('/calculator', defaults={'cid': 0})
    @route('/calculator/<int:cid>')
    def calculator_permalink(self, cid):
        success, result = helpers.get_template_variables_by_id(cid)

        if not success:
            return Response(json.dumps(
                {
                    'message': result
                }
            )), 404

        template, name, variables = result

        return render_template(template,
                               calculator_name=name,
                               variables=variables)
