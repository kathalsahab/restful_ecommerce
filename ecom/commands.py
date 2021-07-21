import logging
from flask.cli import AppGroup, with_appcontext

from ecom.extensions import db


ecom_cli = AppGroup("ecom", help="ECOM custom CLI commands")

@ecom_cli.command(name="create_database")
def create_database():
    """Create SQL database tables, if not created already."""
    db.create_all()



@ecom_cli.command(name="deploy")
@with_appcontext
def deploy():
    """deploy command used create all necessary tables\
         and insert necessary entries while starting the application.
    """

    # Create Database
    db.create_all()

