from flask import Flask
from blueprints import bp
from datafuncs import setupDB

def createApp(config):
    setupDB()
    app = Flask(__name__)
    app.config.from_mapping(config)
    app.register_blueprint(bp)
    return app


if __name__ == "__main__":
    from waitress import serve

    print("Beginning Webserver")
    app = createApp({})
    serve(app, host="0.0.0.0", port=3000, url_scheme="http")
    # serve(app, host="0.0.0.0", port=8080, url_scheme="https")
    # app.run()
