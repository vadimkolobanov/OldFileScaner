import os
import json
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

DIRECTORIES_FILE = "directories.json"


def load_directories():
    if not os.path.exists(DIRECTORIES_FILE):
        return []
    with open(DIRECTORIES_FILE, "r") as file:
        return json.load(file)


def save_directories(directories):
    with open(DIRECTORIES_FILE, "w") as file:
        json.dump(directories, file)


def get_file_list(directory, days):
    files = []
    cutoff_date = datetime.now() - timedelta(days=days)
    for root, dirs, file_names in os.walk(directory):
        for file_name in file_names:
            file_path = os.path.join(root, file_name)
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mod_time < cutoff_date:
                files.append({"name": file_path, "mod_time": file_mod_time})
    return files


def delete_files(file_paths):
    for file_path in file_paths:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")


@app.route("/", methods=["GET", "POST"])
def index():
    files = []
    days = 10  # Default value
    directories = load_directories()

    if request.method == "POST":
        if "directory" in request.form:
            directory = request.form.get("directory")
            if directory not in directories:
                directories.append(directory)
                save_directories(directories)

        days = int(request.form.get("days", 10))
        files_to_delete = request.form.getlist("delete")

        if files_to_delete:
            delete_files(files_to_delete)

        for directory in directories:
            files.extend(get_file_list(directory, days))

    return render_template("index.html", files=files, days=days, directories=directories)


@app.route("/delete_directory/<path:directory>", methods=["POST"])
def delete_directory(directory):
    directories = load_directories()
    directories.remove(directory)
    save_directories(directories)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
