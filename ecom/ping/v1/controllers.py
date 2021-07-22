from ecom.extensions import db
from ecom.utils import Response


def handle_ping():
    return Response.success("Pong")
