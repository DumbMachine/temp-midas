from flask import Flask, flash, redirect, render_template, request, session, abort

app = Flask(__name__)

try:
    from flask_ngrok import run_with_ngrok
    run_with_ngrok(app)  # Start ngrok when app is run
except ImportError:
    pass


# TODO: Move to utils
def prepare_data(location):
    """[summary]

    Args:
        location (string): Location of the csv
    """
    import pandas as pd
    df = pd.read_csv(location)
    if "Progress" not in df.columns:
        df["Progress"] = False
        df.to_csv(location, header=True, index=False)

    return df

df = prepare_data("SA_wrt_WordList_Sample.csv")

@app.route("/")
def hello():
    return render_template("main.html"), 200

@app.route("/receive", methods=["POST"])
def receive():
    files = request.files.items()
    for _, file in files:
        filename = file.filename
        print(filename, _.title())
        # print(dir(filename), _.title())
        file.save(filename+".wav")
    return "temp", 200

@app.route("/front")
def front():
    limit = 10
    rows = []

    for _, row in df.iterrows():
        if _ == limit:
            break
        if row.Progress is False:
            rows.append(row.values)

    return render_template(
        "front.html", 
        foobar=rows,
    ) , 200

@app.route("/item/<int:value>")
def imte_display(value):
    row = df.iloc[value]

    return render_template(
        "main.html", 
        SampleAnswer=row['Sample Answer'],
        QuestionID=row['QuestionID'],
        Category=row['Category'],
        Progress=row['Progress']
    ) , 200

if __name__ == "__main__":
    app.run(debug=True)