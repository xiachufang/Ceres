from ceres.app import app
from ceres.config import AppConfig

if __name__ == "__main__":
    app.run(debug=AppConfig.DEBUG, port=16161)
