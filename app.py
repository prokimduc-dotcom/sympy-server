from flask import Flask, request, jsonify
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
import os

app = Flask(__name__)

# API KEY (đặt trên Render Environment Variables)
API_KEY = os.environ.get("API_KEY", "123456")

transformations = (
    standard_transformations +
    (implicit_multiplication_application,) +
    (convert_xor,)
)

def check_api_key(req):
    key = req.args.get("apikey")
    return key == API_KEY

@app.route("/")
def home():
    return """
    <h2>SymPy CAS Pro Running</h2>
    <p>Use /calc?expr=...</p>
    """

@app.route("/calc")
def calculate():

    if not check_api_key(request):
        return jsonify({"error": "Invalid API Key"}), 403

    expr = request.args.get("expr")
    if not expr:
        return jsonify({"error": "Missing expression"})

    try:
        # Tạo nhiều biến tự động
        symbols = sp.symbols('x y z a b c')
        local_dict = {str(s): s for s in symbols}

        # Phương trình
        if "=" in expr:
            left, right = expr.split("=")
            left_expr = parse_expr(left, transformations=transformations, local_dict=local_dict)
            right_expr = parse_expr(right, transformations=transformations, local_dict=local_dict)

            solutions = sp.solve(left_expr - right_expr, symbols)

            steps = [
                "Move all terms to one side",
                f"{sp.latex(left_expr - right_expr)} = 0",
                "Solve equation"
            ]

            return jsonify({
                "solution": str(solutions),
                "latex": sp.latex(solutions),
                "steps": steps
            })

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
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
