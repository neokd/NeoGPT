import math

from flask import Flask, request

app = Flask(__name__)


@app.route("/calculate", methods=["GET", "POST"])
def calculate():
    if request.method == "GET":
        return """
                <h1>Calculator</h1>

                <form method="post" action="/calculate">
                    Operation:<br>
                    <input type="text" name="operation"><br><br>
                    num1:<br>
                    <input type="float" name="num1"><br><br>
                    num2:<br>
                    <input type="float" name="num2"><br><br>
                    <input type="submit" value="Calculate">
                </form>"""
    else:
        operation = request.form["operation"]
        num1 = float(request.form["num1"])
        num2 = float(request.form["num2"])

        if operation == "add":
            result = num1 + num2
        elif operation == "subtract":
            result = num1 - num2
        elif operation == "multiply":
            result = num1 * num2
        elif operation == "divide":
            result = num1 / num2
        else:
            result = "Invalid operation"

        return f"""<h1>Result: {result}</h1>"""


if __name__ == "__main__":
    app.run()
