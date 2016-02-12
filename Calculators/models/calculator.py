import ContentRelevance.app.db as db

from unique_mixin import UniqueMixin

'''
    Association table for calculators and tags
'''
calculator_tags = db.Table(
    'calculator_tag', db.Model.metadata,
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('calculator_id', db.Integer, db.ForeignKey('calculator.id'))
)


class Tag(db.Model, UniqueMixin):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)

    # e.g. 'interest', or 'compound', or 'finance'
    name = db.Column(db.String())


class Calculator(db.Model):
    __tablename__ = 'calculator'

    id = db.Column(db.Integer, primary_key=True)

    # e.g. 'compound_interest.formula', 'BMI.formula'
    template = db.Column(db.String(), nullable=False)

    # e.g. 'Compound Interest', 'Body Mass Index'
    name = db.Column(db.String(), nullable=False)

    # All tags associated with this calculator
    tags = db.relationship('Tag',
                           secondary='calculator_tag',
                           collection_class=set,
                           backref='calculators')
