from flask import Flask, request
app = Flask(__name__)
app.route("/", methods=["GET"])
def add():
    print("Hello")

if __name__ == '__main__':
    app.run()