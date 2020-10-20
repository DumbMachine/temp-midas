from pathlib import Path
from config import Config
from flask import Flask, request, render_template

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    return app

app = create_app()

try:
    from flask_ngrok import run_with_ngrok
    run_with_ngrok(app)  # was for demo, will be removed later
except ImportError:
    pass


# TODO: Move to utils
def prepare_data():
    """[summary]

    Args:
        location (string): Location of the csv
    """
    import pandas as pd
    df = pd.read_csv(app.config["DATASET_LOCATION"])
    if "Annotators" not in df.columns:
        df["Annotators"] = "<start>"
        df.to_csv(app.config["DATASET_LOCATION"], header=True, index=False)

    return df

df = prepare_data()

# TODO: Skip on error
@app.route("/receive", methods=["POST"])
def receive():
    global df

    files = request.files.items()
    for _, file in files:
        tempname = file.filename
        file_itr, visitorId = tempname.split(",")
        filename = Path(app.config["UPLOAD_FOLDER"])/f"{file_itr}-{visitorId}.wav"
        file.save(str(filename))
        # df.loc[df['index'] == int(filename), "Progress"] = True
        temp = df.loc[df['index'] == int(file_itr), "Annotators"].values[0]
        if visitorId not in temp:
            df.loc[df['index'] == int(file_itr), "Annotators"] = temp + "," + visitorId
        df.to_csv(app.config["DATASET_LOCATION"], header=True, index=False)

    df = prepare_data()

    return "temp", 200

@app.route("/home/<string:username>")
def home(username):
    limit = 10
    done_rows = []
    not_done_rows = []

    for _, row in df.iterrows():
        if limit == 0:
            break
        if username in row.Annotators:
            done_rows.append(row.values)
        else:
            limit -= 1
            not_done_rows.append(row.values)

    return render_template(
        "home.html", 
        done_rows=done_rows,
        not_done_rows=not_done_rows,
    ) , 200

@app.route("/")
def change_name():
    return render_template(
            "name.html", 
        ) , 200


@app.route("/item/<int:value>")
def imte_display(value):
    try:
        row = df.iloc[value]
    except IndexError:
        return render_template(
                "404.html", 
                reason="Item Not Found"
            ) , 404

    return render_template(
        "recording.html", 
        SampleAnswer=row['Sample Answer'],
        QuestionID=row['QuestionID'],
        Category=row['Category'],
        NextValue=value+1,
        PreviousValue=value-1
    ) , 200

if __name__ == "__main__":
    try:
        run_with_ngrok
        app.run()
    except Exception:
        app.run(host="0.0.0.0", port=5420, debug=True)