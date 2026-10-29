from flask import Flask, jsonify

from claims import claims
from items import items


def create_app():
    app = Flask(__name__)
    app.register_blueprint(items, url_prefix="/api")
    app.register_blueprint(claims, url_prefix="/api")

    @app.errorhandler(Exception)
    def handle_error(e):
        return jsonify({"error": str(e)}), 500

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Admin-Token, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST,DELETE, OPTIONS"
        return response

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
