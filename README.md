# Calculators

Can we write a universal calculator repository? Looks like we can!

## To run

1. Install libraries, see `requirements.txt` section below.

    a. If you're using a virtualenv, activate it before running

2. Run! From the top level of the repository, `python run.py [--debug]`

## Calculators

The calculators that are currently defined are Compound Interest and Body Mass Index.

Calculators can be added to `Calculators/templates/formulae`.

To render the calculator, point the app at the formula file, e.g. `localhost:8080/compound_interest`
for `compound_interest.formula`, `localhost:8080/BMI` for `BMI.formula`. Currently, `localhost:8080/`
renders the compound interest calculator.

## Important files

    - requirements.txt
    - run.py
    - Calculators
        - __init__.py
        - helpers.py
        - models
            - calculator.py
        - templates
            - calculator.html
            - formulae
                - BMI.formula
                - compound_interest.formula
        - views
            - calculator
                - Calculator.py
            - endpoint
                - Endpoint.py

#### `requirements.txt`

Python libraries used by the app. To install them, run `pip install -r requirements`. We suggest
using a virtual environment so that you don't have to install the libraries system-wide. This would
look something like

    virtualenv .env
    . ./.env/bin/activate
    pip install -r requirements.txt

#### `run.py`

Used to run the app. Takes an optional command line argument `--debug` to enable Flask debug mode.

#### `Calculators/__init__.py`

Contains the Flask app variable and some setup code

#### `Calculators/helpers.py`

Contains helper functions. Currently, the only helper function is `get_template_variables`, which
reads a Jinja2 template representing a calculator formula and returns the variables that need to
be filled in.

#### `Calculators/models/calculator.py`

Contains an SQLAlchemy declarative definition of the database tables for this app.

#### `templates/calculator.html`

The template file for a generic calculator.

#### `templates/formulae`

Contains `.formula` files, which define a specific calculator.

#### `views`

Sets up different endpoints for the app.

##### `view/calculator/Calculator.py`

Defines the index page of the app, which renders a calculator as a form.

##### `view/endpoint/Endpoint.py`

Defines the API for the app.

## Remaining work, in no particular order

* Fix up all of the TODOs
* Make the form pretty
* Create some unit tests
* Add a backend for formula maintenance. I'm imagining a code editor, easily adding and removing tags, etc.
