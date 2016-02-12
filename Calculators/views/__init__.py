from Calculators import app

from endpoint import Endpoint
from calculator import Index


def register_views():
    Endpoint.register(app)
    Index.register(app)
