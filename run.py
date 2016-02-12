#!/usr/bin/python

import sys

from Calculators import app

debug = '--debug' in sys.argv
app.run(host='0.0.0.0', debug=debug, port=8080 if debug else 80)
