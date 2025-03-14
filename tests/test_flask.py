from flask import Flask

app = Flask(__name__)

@app.route("/health", methods=('GET', 'POST'))
def index():
    return "Congratulations, it's a web app!"
#, debug=True
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9086)

print("finish")