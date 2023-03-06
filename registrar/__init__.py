from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    from . import handler

    app.register_blueprint(handler.bp)

    return app
