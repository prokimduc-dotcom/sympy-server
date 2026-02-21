from flask import Flask, request, jsonify
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
import os
import re

app = Flask(__name__)

# ====== SECURITY ======
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not set in environment variables")

def check_api_key(req):
    return req.args.get("apikey") == API_KEY


# ====== PARSER SETTINGS ======
transformations = (
    standard_transformations +
    (implicit_multiplication_application,) +
    (convert_xor,)
)


# ====== AUTO DETECT VARIABLES ======
def extract_symbols(expr):
    names = set(re.findall(r"[a-zA-Z]+", expr))
    symbols = {name: sp.symbols(name) for name in names}
    return symbols


@app.route("/")
def home():
    return """
    <h2>SymPy CAS Pro Running</h2>
    <p>Use /calc?apikey=YOUR_KEY&expr=...</p>
    """


@app.route("/calc")
def calculate():

    if not check_api_key(request):
        return jsonify({"error": "Invalid API Key"}), 403

    expr = request.args.get("expr")
    if not expr:
        return jsonify({"error": "Missing expression"}), 400

    try:
        local_dict = extract_symbols(expr)

        # ====== HANDLE EQUATION ======
        if "=" in expr:
            left, right = expr.split("=", 1)

            left_expr = parse_expr(left, transformations=transformations, local_dict=local_dict)
            right_expr = parse_expr(right, transformations=transformations, local_dict=local_dict)

            equation = left_expr - right_expr

            variables = list(local_dict.values())

            solutions = sp.solve(equation, variables, dict=True)

            steps = [
                "Move all terms to one side",
                sp.latex(equation) + " = 0",
                "Solve equation"
            ]

            return jsonify({
                "solution": str(solutions),
                "latex": sp.latex(solutions),
                "steps": steps
            })

        # ====== NORMAL EXPRESSION ======
        parsed = parse_expr(expr, transformations=transformations, local_dict=local_dict)

        simplified = sp.simplify(parsed)

        steps = [
            "Original expression:",
            sp.latex(parsed),
            "After simplification:",
            sp.latex(simplified)
        ]

        return jsonify({
            "result": str(simplified),
            "latex": sp.latex(simplified),
            "steps": steps
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
