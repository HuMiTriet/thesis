from proxy import proxies
from flask import Flask
import requests


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    from . import resource

    app.register_blueprint(resource.bp)

    return app
