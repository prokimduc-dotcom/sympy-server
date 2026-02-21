from flask import Flask, request, jsonify
import sympy as sp
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "SymPy Server is running!"

@app.route("/calc")
def calculate():
    expr = request.args.get("expr")
    if not expr:
        return jsonify({"error": "Missing expression"})
    
    try:
        x = sp.symbols('x')
        result = sp.simplify(expr)
        return jsonify({"result": str(result)})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
