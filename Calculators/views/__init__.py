from Calculators import app

from edit import Edit
from endpoint import Endpoint
from calculator import Index


def register_views():
    Edit.register(app)
    Endpoint.register(app)
    Index.register(app)
