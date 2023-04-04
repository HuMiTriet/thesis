from dotenv import load_dotenv
from flask import Flask
from werkzeug.exceptions import InternalServerError

from lamport_clock import LamportClock


lamportClock = LamportClock()


def create_app():

    load_dotenv()
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    @app.errorhandler(InternalServerError)
    def custom_error_msg(error: InternalServerError):  # pyright: ignore
        return f"SERVER Err {str(error.__repr__)}", 500

    from . import resource  # pylint: disable=import-outside-toplevel

    app.register_blueprint(resource.bp)

    return app
