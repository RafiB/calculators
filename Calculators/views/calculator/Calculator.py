from flask.ext.classy import FlaskView

from flask import (
    render_template,
)


class Index(FlaskView):
    route_base = '/'

    def index(self):
        return render_template('calculator.html')
