# api.py  (inside auto-Uppaal/src)

from flask import Flask, request, jsonify
from flask_cors import CORS

from pipeline import AutoPipeline  # your existing class

app = Flask(__name__)
CORS(app)  # allow requests from localhost:5173 (Vite)

pipeline = AutoPipeline()


@app.post("/generate")
def generate():
    """
    JSON body:
    {
      "description": "model description text",
      "queries": ["A[] not deadlock", "E<> P.S"]
    }
    """
    data = request.get_json(force=True) or {}
    description = (data.get("description") or "").strip()
    queries = data.get("queries") or []

    if not description:
        return jsonify({"success": False, "error": "description is required"}), 400
    if not isinstance(queries, list):
        return jsonify({"success": False, "error": "queries must be a list"}), 400
    if not queries:
        # default safety property if user didn't provide any
        queries = ["A[] not deadlock"]

    try:
        ok, attempts, verifier_msg, xml = pipeline.run(description, queries)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    return jsonify(
        {
            "success": bool(ok),
            "attempts": attempts,
            "xml": xml,
            "verifier_log": verifier_msg,
        }
    )


if __name__ == "__main__":
    # Run on http://localhost:5000
    app.run(host="127.0.0.1", port=5000, debug=True)
