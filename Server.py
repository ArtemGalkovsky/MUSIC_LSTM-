"""
Main File. Creates Server and Starts it.
"""
from flask import Flask, render_template, session, request, jsonify, redirect, url_for, send_from_directory
from nn import train
from multiprocessing import Process, freeze_support
from uuid import uuid4
from os import system

# Create Server

app = Flask(__name__, template_folder="web/templates")
app.static_folder = "web/static"
app.config["SECRET_KEY"] = "09e709707340973307409734v07v3409vb03v773v"
app.config["UPLOAD_FOLDER"] = "web/Upload"
processes = {}
langs = ("en", "ru")


# Initializing routes

@app.route("/sys/get-proc-info", methods=["POST"])
def get_process_info():
    """
    Function sends info about the process.
    :return: json
    """
    proc_id = request.get_json(force=True)["proc_id"]
    json = jsonify(processes[proc_id]["json"])
    if processes[proc_id]["json"] and processes[proc_id]["json"][-1]["text"]["msg_type"] != "audio ready":
        processes[proc_id]["json"] = []
    return json


@app.route("/sys/update-proc-info", methods=["POST"])
def set_process_info():
    """
    Set information about a process.
    :return: None.
    """

    js = request.get_json(force=True)
    processes[js["proc_id"]]["json"].append(js)

    return "OK"


@app.route("/sys/data-ready", methods=["POST"])
def data_ready():
    """
    Function for creating a process for a neural network.
    :return: redirect
    """
    from os import path
    data = request.form.to_dict()
    file = request.files["file"]
    file.save(path.join(app.config['UPLOAD_FOLDER'], file.filename))

    session["process"] = str(uuid4())

    proc = Process(target=train, args=((data, file.filename, session["process"]),))
    processes[session["process"]] = {"proc": proc, "json": []}
    proc.start()

    if session.get("lang"):
        return redirect(f"/training/{session['lang']}")

    return redirect("/training/en")


def get_lang_json(lang, page):
    """

    :param lang: language (ru, en...): str;
    :param page: page name (main, training): str;
    :return: json with translation.
    """
    from json import load
    with open(f"web/static/lang/{lang}.json", encoding="UTF-8") as fl:
        translation = load(fl)

    return translation[page]


@app.route("/")
def main_page():
    """
    Render Lang Choose Page.
    :return: HTML.
    """
    return render_template("lang_choose.html")


@app.route("/main/<string:lang>")
def main(lang):
    """
    Render Main Page.
    :param lang: language: str;
    :return: Main Page HTML / Invalid Lang (400).
    """
    if lang in langs:
        session["lang"] = lang
        return render_template("index.html",
                               **get_lang_json(lang, "main"))

    return "Invalid Lang (Неизвестный Язык)!", 400


@app.route("/training/<string:lang>")
def training(lang):
    """
    Render Training Page.
    :param lang: language: str;
    :return: Train HTML / redirect('/')
    """
    if lang in langs and session["process"]:
        return render_template("train.html", proc_id=session["process"], **get_lang_json(lang, "train"))

    return redirect("/")


# Starting Server

if __name__ == "__main__":
    freeze_support()
    system("start http://127.0.0.1:1000")
    app.run(debug=True, host="127.0.0.1", port="1000")