from dotenv import load_dotenv
from flask import Flask
from werkzeug.exceptions import InternalServerError


resource_currently_using: set[str] = set()


def create_app():
    """
    The factory function that returns an instance of the client.

    A client is an entity that interact with a resource in acquiring locks and
    or releasing it.
    """
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)

    # pylint: disable=import-outside-toplevel
    from . import gossip

    app.register_blueprint(gossip.bp)

    @app.errorhandler(InternalServerError)
    def custom_error_msg(error: InternalServerError):  # pyright: ignore
        return f"CLIENT Err {str(error.__repr__)}", 500

    return app
