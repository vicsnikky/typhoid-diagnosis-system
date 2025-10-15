# app.py
from flask import Flask, render_template, request, jsonify
from rule_engine import RuleEngine
from models import SubmissionModel
from pydantic import ValidationError
import uuid
import json

app = Flask(__name__, static_folder="static", template_folder="templates")
engine = RuleEngine("rules.yaml")

# In-memory store for demonstration (resets when server restarts)
IN_MEMORY_DB = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/submit", methods=["POST"])
def submit():
    try:
        payload = request.get_json()
        if payload is None:
            return jsonify({"error": "Invalid JSON"}), 400
        # Validate payload
        submission = SubmissionModel(**payload)
    except ValidationError as e:
        return jsonify({"error": "validation_error", "details": json.loads(e.json())}), 422
    except Exception as e:
        return jsonify({"error": "bad_request", "message": str(e)}), 400

    submission_dict = submission.dict()
    result = engine.evaluate(submission_dict)

    # optionally store (only if consent_store True)
    submission_id = str(uuid.uuid4())
    IN_MEMORY_DB[submission_id] = {
        "submission": submission_dict,
        "result": result
    }

    response = {
        "submission_id": submission_id,
        "result": result
    }
    return jsonify(response), 200

@app.route("/api/submission/<submission_id>", methods=["GET"])
def get_submission(submission_id):
    rec = IN_MEMORY_DB.get(submission_id)
    if not rec:
        return jsonify({"error": "not_found"}), 404
    return jsonify(rec), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
