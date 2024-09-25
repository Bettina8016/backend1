from flask import Flask
# from routes.auth import auth_routes
from functions import function_routes
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Registering routes
# app.register_blueprint(auth_routes)
app.register_blueprint(function_routes)

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=8080, debug=True)