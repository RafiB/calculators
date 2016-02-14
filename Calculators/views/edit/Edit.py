from flask.ext.classy import FlaskView

from flask import (
    render_template,
)


class Edit(FlaskView):
    def index(self):
        return render_template('edit_calculators.html')
