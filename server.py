import sqlite3
from pathlib import Path
from config import Config
from flask import Flask, jsonify, request, render_template


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    return app


def get_db():
    con = sqlite3.connect("data.sqlite")

    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    if ("user",) not in cursor.fetchall():
        cursor.execute("CREATE TABLE user (username TEXT, progress TEXT)")

    return con


app = create_app()

try:
    from flask_ngrok import run_with_ngrok
    run_with_ngrok(app)  # Start ngrok when app is run
except ImportError:
    pass



@app.route("/")
def change_name():
    return (
        render_template("name.html", username=None),
        200,
    )


@app.route("/home/<string:username>")
def home(username):
    try:
        LIMIT = 10
        done_rows = []
        not_done_rows = []

        db = get_db()
        user_exists = db.execute(
            # f"SELECT username FROM user"
            f"SELECT username FROM user where username='{username}'"
        ).fetchall()
        if user_exists == []:
            # create the user information
            db.execute(
                f"INSERT INTO user (username, progress) values ('{username}', 0)"
            )
            app.logger.info(f"Add user to database: {username}")

        # getting remaining items
        done_indexes = (
            db.execute(f"SELECT progress FROM user where username='{username}'")
            .fetchone()[0]
            .split(",")
        )

        # getting remaining ones
        indexes = db.execute(f"SELECT id FROM data")
        for index in indexes:
            index_str = index[0]
            row = db.execute(f"SELECT * FROM data WHERE id='{index_str}'").fetchone()
            if index_str in done_indexes:
                done_rows.append(row)
            else:
                not_done_rows.append(row)

    except Exception as e:
        app.logger.error(e)
        return (
            render_template(
                "404.html",
                reason=str(e),
            ),
            404,
        )

    db.commit()

    return (
        render_template(
            "home.html",
            done_rows=done_rows,
            not_done_rows=not_done_rows[:LIMIT],
            len_total=len(done_rows) + len(not_done_rows),
            done_rows_len=len(done_rows),
            not_done_rows_len=len(not_done_rows),
        ),
        200,
    )


# TODO: Skip on error
@app.route("/receive", methods=["POST"])
def receive():
    try:
        db = get_db()
        files = request.files.items()
        for _, file in files:
            tempname = file.filename
            file_itr, username = tempname.split(",")
            filename = Path(app.config["UPLOAD_FOLDER"]) / f"{file_itr}-{username}.wav"
            file.save(str(filename))

            # updating the user column
            curr_progress = db.execute(
                f"SELECT progress FROM user where username='{username}'"
            ).fetchone()
            curr_progress = curr_progress[0]
            progress_string = curr_progress + "," + file_itr
            db.execute(
                f"UPDATE user SET progress='{progress_string}' WHERE username='{username}'"
            )
            app.logger.info(f"Added annotation: {file_itr} to username: {username}")
            db.commit()

    except Exception as e:
        jsonify(message=str(e)), 500

    return (
        jsonify(
            message=f"Audio uploaded succesfully for user: {username}",
            type="AUDIO_ADDED",
        ),
        200,
    )


@app.route("/item/<int:value>")
def recording_display(value):
    db = get_db()
    row = db.execute(f"SELECT * FROM data WHERE id='{value}'").fetchone()
    if not row:
        return (
            render_template("404.html", reason=f"Recording #{value} was not Found"),
            404,
        )

    return (
        render_template(
            "recording.html",
            SampleAnswer=row[3],
            QuestionID=row[1],
            Category=row[2],
            NextValue=value + 1,
            PreviousValue=value - 1,
        ),
        200,
    )


@app.route("/404")
def error_site():
    return (
        render_template(
            "404.html",
        ),
        404,
    )


if __name__ == "__main__":
    try:
        run_with_ngrok
        app.run()
    except Exception:
        app.run(host="0.0.0.0", port=6420, debug=True)