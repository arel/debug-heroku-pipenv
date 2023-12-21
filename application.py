import os
import logging
from mypackage.mymodule import are_you_there
from flask import Flask


logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
)

app.logger.setLevel(logging.DEBUG)

@app.route("/", methods=["GET"])
def index():
    return f"Do I work? {are_you_there()}", 200

if __name__ == "__main__":
    app.run(debug=True, port=8000, host="0.0.0.0")
