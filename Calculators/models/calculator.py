from Calculators import app

'''
    Association table for calculators and tags
'''
calculator_tags = app.db.Table(
    'calculator_tag', app.db.Model.metadata,
    app.db.Column('tag_id', app.db.Integer, app.db.ForeignKey('tag.id')),
    app.db.Column('calculator_id', app.db.Integer, app.db.ForeignKey('calculator.id'))
)


class Tag(app.db.Model):
    __tablename__ = 'tag'

    id = app.db.Column(app.db.Integer, primary_key=True)

    # e.g. 'interest', or 'compound', or 'finance'
    name = app.db.Column(app.db.String())


class Calculator(app.db.Model):
    __tablename__ = 'calculator'

    id = app.db.Column(app.db.Integer, primary_key=True)

    # e.g. 'compound_interest.formula', 'BMI.formula'
    template = app.db.Column(app.db.String(), nullable=False)

    # e.g. 'Compound Interest', 'Body Mass Index'
    name = app.db.Column(app.db.String(), nullable=False)

    # All tags associated with this calculator
    tags = app.db.relationship('Tag',
                           secondary='calculator_tag',
                           collection_class=set,
                           backref='calculators')
