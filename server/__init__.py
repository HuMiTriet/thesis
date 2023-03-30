from flask import Flask


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    from . import resource  # pylint: disable=import-outside-toplevel

    app.register_blueprint(resource.bp)

    return app
