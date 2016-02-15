import os
import ast
import json
import errno
import functools

from Calculators import helpers
from Calculators.models import Calculator, Tag

from flask import (
    current_app,
    redirect,
    render_template,
    Response,
    request,
    url_for,
)

from flask.ext.classy import FlaskView, route

from sqlalchemy import func, or_

from voluptuous import Coerce, Schema, MultipleInvalid


def validate_form_has_okay_id(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        got_id = Schema({'id': Coerce(int)}, required=True, extra=True)

        try:
            got_id(request.values)
        except MultipleInvalid:
            return Response(json.dumps(
                {
                    'message': 'You must include a calculator id in the POST '
                    'data.'
                }
            )), 400

        if not Calculator.query.get(request.values['id']):
            return Response(
                "Can't find calculator #{:}".format(request.values['id'])), 404

        return f(*args, **kwargs)
    return wrapper


def validate_form_has_template(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        got_formula = Schema({'formula': basestring}, required=True, extra=True)

        try:
            got_formula(request.values)
        except MultipleInvalid:
            return Response(json.dumps(
                {
                    'message': 'You must include a calculator id and formula '
                    'in the POST data.'
                }
            )), 400

        return f(*args, **kwargs)
    return wrapper


def validate_form_has_name(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        got_name = Schema({'name': basestring}, required=True, extra=True)

        try:
            got_name(request.form)
        except MultipleInvalid:
            return Response(json.dumps(
                {
                    'message': 'You must include a name in the PUT data.'
                }
            )), 400

        return f(*args, **kwargs)
    return wrapper


def format_calculators(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        calculators = f(*args, **kwargs)

        return json.dumps({
            'results': [
                {'id': c.id,
                 'name': c.name,
                 'link': url_for('Endpoint:get_calculator_variables', cid=c.id,
                                 _external=True)} for c in calculators],
            'size': len(calculators)
        })
    return wrapper


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

    @route('/calculator')
    @format_calculators
    def dump_calculators(self):
        return Calculator.query.all()

    @route('/calculator/<int:cid>/variables')
    def get_calculator_variables(self, cid):
        calculator = Calculator.query.get(cid)

        if not calculator:
            return Response("Can't find calculator #{:}".format(cid)), 404

        template = os.path.join('formulae', calculator.template)

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

        calculators = Calculator.query.filter(
            or_(
                or_(*[func.lower(Calculator.name).like('%'+t+'%')
                      for t in search_tags]),
                Calculator.tags.any(
                    or_(*[func.lower(Tag.name).like('%'+t+'%')
                        for t in search_tags])
                )
            )
        ).all()

        calculators = [
            {
                'name': c.name,
                'tags': list(set([t.name for t in c.tags for tag in search_tags
                                  if tag in t.name.lower()])),
                'id': c.id
            }
            for c in calculators]

        calculators = sorted(
            calculators,
            key=lambda x: (search_string in x['name'].lower(), len(x['tags'])),
            reverse=True)

        return json.dumps(calculators)

    @route('/seach_tags/<search>')
    def search_tags(self, search):
        search = search.lower()
        tags = Tag.query.filter(func.lower(Tag.name).like('%'+search+'%')).all()

        tags = [search] + sorted([tag.name for tag in tags
                                  if tag.name != search])

        return json.dumps(tags)

    @route('/get_html_form_by_id', methods=['POST'])
    @validate_form_has_okay_id
    def get_html_form_by_id(self):
        # TODO is it better to return rendered HTML, or a JSON dict for the JS
        # to create the form?
        return redirect(url_for('Index:calculator_permalink_0',
                                cid=request.form['id']))

    @route('/get_formula')
    @validate_form_has_okay_id
    def get_formula(self):
        cid = request.values['id']
        calculator = Calculator.query.get(cid)
        template = os.path.join(current_app.root_path, 'templates', 'formulae',
                                calculator.template)

        with open(template) as f:
            return json.dumps(
                {
                    'template': f.read().strip(),
                    'tags': sorted([t.name for t in calculator.tags])
                }
            )

    @route('/set_tags', methods=['POST'])
    @validate_form_has_okay_id
    def set_tags(self):
        cid = request.form['id']
        calculator = Calculator.query.get(cid)
        calculator.tags.clear()  # = set([])
        for tag_text in json.loads(request.form.get('tags', '[]')):
            tag = helpers.get_or_create(current_app.db.session, Tag,
                                        name=tag_text)
            calculator.tags.add(tag)

        # Delete any tags that aren't associated with a calculator
        Tag.query.filter(~Tag.calculators.any()).delete(
            synchronize_session=False)

        current_app.db.session.commit()
        return 'Done', 200

    @route('/set_formula', methods=['POST'])
    @validate_form_has_okay_id
    @validate_form_has_template
    def set_formula(self):
        cid = request.form['id']
        calculator = Calculator.query.get(cid)
        helpers.write_template_file(calculator.template,
                                    formula=request.form['formula'])

        return json.dumps({'message': 'Saved!'})

    @route('/new_formula', methods=['PUT'])
    @validate_form_has_name
    @format_calculators
    def new_formula(self):
        calculator = Calculator(
            name=request.form['name'],
            template=request.form['name'].lower().replace(' ', '_') + '.formula'
        )

        current_app.db.session.add(calculator)
        try:
            current_app.db.session.commit()
        except:
            return Response(json.dumps(
                {
                    'message': 'There was an error creating the new calculator'
                }
            )), 500

        helpers.write_template_file(calculator.template)

        return [calculator]

    @route('/delete_calculator', methods=['DELETE'])
    @validate_form_has_okay_id
    def delete_calculator(self):
        calculator = Calculator.query.get(request.form['id'])

        template = os.path.join(current_app.root_path, 'templates',
                                'formulae', calculator.template)
        try:
            os.remove(template)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

        Calculator.query.filter_by(id=request.form['id']).delete()

        current_app.db.session.commit()

        return 'Calculator #{:} deleted'.format(request.form['id'])
