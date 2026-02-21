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

# Cho phép viết 2x, x^2
transformations = (
    standard_transformations +
    (implicit_multiplication_application,) +
    (convert_xor,)
)

@app.route("/")
def home():
    return "SymPy CAS Mini is running!"

@app.route("/calc")
def calculate():
    expr = request.args.get("expr")
    if not expr:
        return jsonify({"error": "Missing expression"})

    try:
        x = sp.symbols('x')

        # Nếu là phương trình có dấu =
        if "=" in expr:
            left, right = expr.split("=")
            left_expr = parse_expr(left, transformations=transformations)
            right_expr = parse_expr(right, transformations=transformations)
            solution = sp.solve(left_expr - right_expr, x)
            return jsonify({"solution": str(solution)})

        # Đạo hàm
        if expr.startswith("diff("):
            inside = expr[5:-1]
            parsed = parse_expr(inside, transformations=transformations)
            result = sp.diff(parsed, x)
            return jsonify({"derivative": str(result)})

        # Tích phân
        if expr.startswith("integrate("):
            inside = expr[10:-1]
            parsed = parse_expr(inside, transformations=transformations)
            result = sp.integrate(parsed, x)
            return jsonify({"integral": str(result)})

        # Tính giá trị nếu có x=...
        if "," in expr:
            expression_part, value_part = expr.split(",")
            parsed = parse_expr(expression_part, transformations=transformations)
            var, val = value_part.split("=")
            result = parsed.subs(x, float(val))
            return jsonify({"value": str(result)})

        # Mặc định: simplify
        parsed = parse_expr(expr, transformations=transformations)
        result = sp.simplify(parsed)
        return jsonify({"result": str(result)})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
