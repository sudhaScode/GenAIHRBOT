from multiprocessing.managers import BaseManager
from flask import Flask, request
import json
import os



# initialize manager connection
with open("config.json", "r") as f:
  config = json.load(f)

password = config["password"].encode()

manager = BaseManager(("", config["server_port"]), password)
manager.register("query_index")
manager.connect()

app = Flask(__name__)

@app.route("/query", methods=["GET"])
def query_index():
    global index
    query_text = request.args.get("text", None)
    if query_text is None:
        return (
            "No text found, please include a ?text=blah parameter in the URL",
            400,
        )
    response = manager.query_index(query_text)._getvalue()
    return str(response), 200


@app.route("/")
def home():
    return "Hello World!"

...
manager.register("insert_into_index")
...


@app.route("/uploadFile", methods=["POST"])
def upload_file():
    global manager
    if "file" not in request.files:
        return "Please send a POST request with a file", 400

    filepath = None
    try:
        uploaded_file = request.files["file"]
        filename = uploaded_file.filename
        filepath = os.path.join("documents", os.path.basename(filename))
        uploaded_file.save(filepath)

        if request.form.get("filename_as_doc_id", None) is not None:
            manager.insert_into_index(filepath, doc_id=filename)
        else:
            manager.insert_into_index(filepath)
    except Exception as e:
        # cleanup temp file
        if filepath is not None and os.path.exists(filepath):
            os.remove(filepath)
        return "Error: {}".format(str(e)), 500

    # cleanup temp file
    if filepath is not None and os.path.exists(filepath):
        os.remove(filepath)

    return "File inserted!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5601)

#flask --app flask_server run