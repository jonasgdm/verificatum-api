from flask import Flask
from routes import routes_bp  # importa o blueprint de rotas
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.register_blueprint(routes_bp)  # registra o blueprint

if __name__ == "__main__":
    app.run(debug=True, port=5000)
