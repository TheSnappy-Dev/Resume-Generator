from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import datetime
import jwt
from werkzeug.security import check_password_hash

# Configuration from environment
JWT_SECRET = os.getenv("JWT_SECRET", None)
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET must be set in environment")

AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
AUTH_PASSWORD_HASH = os.getenv("AUTH_PASSWORD_HASH", None)
if not AUTH_PASSWORD_HASH:
    raise RuntimeError("AUTH_PASSWORD_HASH (werkzeug hash) must be set in environment")

# Third-party API key for resume generation (e.g. OpenAI or PDF service)
RESUME_API_KEY = os.getenv("RESUME_API_KEY", None)
# If your service requires an API key, ensure RESUME_API_KEY is set.
# You can still run the server without it if you replace the resume generation logic with a mock.

app = Flask(__name__)
CORS(app)


def token_required(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Authorization header missing or malformed"}), 401
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = payload.get("sub")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except Exception:
            return jsonify({"error": "Invalid token"}), 401
        return fn(*args, **kwargs)

    return wrapper


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    if username != AUTH_USERNAME or not check_password_hash(AUTH_PASSWORD_HASH, password):
        return jsonify({"error": "invalid credentials"}), 401

    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    token = jwt.encode({"sub": username, "exp": exp}, JWT_SECRET, algorithm="HS256")
    # PyJWT returns bytes for older versions; ensure string
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return jsonify({"token": token, "expires_at": exp.isoformat()})


@app.route("/generate", methods=["POST"])
@token_required
def generate_resume():
    payload = request.get_json(force=True)
    # Validate payload fields according to your frontend (e.g., name, experiences, etc.)
    # Example placeholder logic:
    if not payload:
        return jsonify({"error": "missing payload"}), 400

    if not RESUME_API_KEY:
        # If the repo's missing the external API key, return a helpful message
        return (
            jsonify(
                {
                    "error": "Server not configured with third-party API key (RESUME_API_KEY)."
                }
            ),
            500,
        )

    # TODO: Replace the following block with integration with the actual resume/PDF generation API.
    # Example: call OpenAI or a PDF generator using RESUME_API_KEY and return the generated PDF or S3 URL.
    # For now we'll return a mock response to demonstrate protected endpoint.
    result = {
        "status": "ok",
        "message": "Resume generation endpoint reached",
        "user": request.user,
        "received": payload,
    }

    return jsonify(result)


if __name__ == "__main__":
    # Only use debug in development!
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
