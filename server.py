import json
import mimetypes
import shutil
import uuid
from email.parser import BytesParser
from email.policy import default
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from main import process_sheet_music


ROOT = Path(__file__).resolve().parent
UPLOADS_DIR = ROOT / "uploads"
RESULTS_DIR = ROOT / "results"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def is_allowed_dev_origin(origin):
    if not origin:
        return False

    parsed = urlparse(origin)
    if parsed.scheme != "http":
        return False

    if parsed.hostname not in {"127.0.0.1", "localhost"}:
        return False

    return 5173 <= (parsed.port or 0) <= 5199


class OMRRequestHandler(BaseHTTPRequestHandler):
    server_version = "OMRWeb/1.0"

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_cors_headers()
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/process":
            self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return

        try:
            uploaded = self.read_upload()
            result = self.process_upload(uploaded)
            self.send_json(result)
        except Exception as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path.startswith("/api/results/"):
            self.serve_result_file(path.removeprefix("/api/results/"), attachment=False)
            return

        if path.startswith("/api/download/"):
            self.serve_result_file(path.removeprefix("/api/download/"), attachment=True)
            return

        self.send_json({"status": "ok", "message": "OMR API is running."})

    def read_upload(self):
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            raise ValueError("Expected a multipart form upload.")

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        message = BytesParser(policy=default).parsebytes(
            f"Content-Type: {content_type}\r\n\r\n".encode("utf-8") + body
        )

        for part in message.iter_parts():
            if part.get_param("name", header="content-disposition") == "sheet":
                filename = part.get_filename() or "upload.png"
                data = part.get_payload(decode=True)
                if not data:
                    raise ValueError("The uploaded file was empty.")
                return {"filename": filename, "data": data}

        raise ValueError("Upload field 'sheet' was not found.")

    def process_upload(self, uploaded):
        source_name = Path(uploaded["filename"]).name
        extension = Path(source_name).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError("Please upload a PNG, JPG, or JPEG image.")

        job_id = uuid.uuid4().hex
        upload_dir = UPLOADS_DIR / job_id
        result_dir = RESULTS_DIR / job_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        result_dir.mkdir(parents=True, exist_ok=True)

        upload_path = upload_dir / f"sheet{extension}"
        upload_path.write_bytes(uploaded["data"])

        result = process_sheet_music(upload_path, result_dir)
        result["jobId"] = job_id
        result["sourceName"] = source_name
        return result

    def serve_result_file(self, relative_path, attachment):
        parts = [part for part in Path(relative_path).parts if part not in ("", ".", "..")]
        if len(parts) != 2:
            self.send_json({"error": "Invalid file path."}, HTTPStatus.BAD_REQUEST)
            return

        file_path = RESULTS_DIR / parts[0] / parts[1]
        if not file_path.exists() or not file_path.is_file():
            self.send_json({"error": "File not found."}, HTTPStatus.NOT_FOUND)
            return

        mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_cors_headers()
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(file_path.stat().st_size))
        if attachment:
            self.send_header("Content-Disposition", f'attachment; filename="{file_path.name}"')
        self.end_headers()

        with file_path.open("rb") as file:
            shutil.copyfileobj(file, self.wfile)

    def send_json(self, data, status=HTTPStatus.OK):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def send_cors_headers(self):
        origin = self.headers.get("Origin")
        self.send_header(
            "Access-Control-Allow-Origin",
            origin if is_allowed_dev_origin(origin) else "http://127.0.0.1:5173",
        )
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


def run(host="127.0.0.1", port=8000):
    UPLOADS_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)
    server = ThreadingHTTPServer((host, port), OMRRequestHandler)
    print(f"OMR API running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
