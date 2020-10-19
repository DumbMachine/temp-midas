from pathlib import Path
from config import Config
from flask import Flask, render_template

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
    if "Progress" not in df.columns:
        df["Progress"] = False
        df.to_csv(app.config["DATASET_LOCATION"], header=True, index=False)

    return df

df = prepare_data()

@app.route("/receive", methods=["POST"])
def receive():
    global df

    files = request.files.items()
    for _, file in files:
        filename = file.filename
        print(filename, _.title())
        # print(dir(filename), _.title())
        file.save(filename+".wav")
            
        df.loc[df['index'] == int(filename), "Progress"] = True
        df.to_csv(app.config["DATASET_LOCATION"], header=True, index=False)

    df = prepare_data()

    return "temp", 200

@app.route("/")
def front():
    limit = 10
    rows = []

    for _, row in df.iterrows():
        if _ == limit:
            break
        if row.Progress is False:
            rows.append(row.values)

    return render_template(
        "home.html", 
        foobar=rows,
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
        Progress=row['Progress'],
        NextValue=value+1,
        PreviousValue=value-1
    ) , 200

@app.route("/temp")
def temp():
    return render_template(
        "temp.html"
    ) , 200

if __name__ == "__main__":
    """
    ExecStart=/home/ubuntu/microblog/venv/bin/gunicorn -b localhost:8000 -w 4 microblog:app
    """
    try:
        run_with_ngrok
        app.run()
    except Exception:
        app.run(host="0.0.0.0", port=5420, debug=True)