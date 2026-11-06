from flask import Flask, request, send_file, render_template_string
from pypdf import PdfReader, PdfWriter
from io import BytesIO

app = Flask(__name__)

MAX_FILES = 200
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB per PDF

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PDF Merger - 200 Files</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f3f6;
            text-align: center;
            padding: 35px 15px;
            color: #202938;
        }
        .container {
            background: white;
            padding: 35px;
            max-width: 680px;
            margin: auto;
            border-radius: 15px;
            box-shadow: 0 3px 15px #00000018;
        }
        h1 { color: #2459c5; }
        input { margin: 25px 0; max-width: 100%; }
        button {
            background: #2459c5;
            color: white;
            padding: 14px 30px;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #17449e; }
        .note { color: #667085; font-size: 13px; }
    </style>
</head>
<body>
<div class="container">
    <h1>PDF Merger Tool</h1>
    <p>Select between 2 and 200 PDF files to combine them into one PDF.</p>
    <form action="/merge" method="POST" enctype="multipart/form-data">
        <input type="file" name="pdfs" accept=".pdf,application/pdf"
               multiple required>
        <br>
        <button type="submit">MERGE PDF FILES</button>
    </form>
    <p class="note">Files are processed locally on your computer.</p>
    <p class="note">Maximum 200 files; maximum 200 MB per file.</p>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/merge", methods=["POST"])
def merge():
    files = [f for f in request.files.getlist("pdfs") if f and f.filename]

    if len(files) < 2:
        return "Please select at least 2 PDF files.", 400

    if len(files) > MAX_FILES:
        return f"Maximum limit is {MAX_FILES} PDF files.", 400

    writer = PdfWriter()

    try:
        for uploaded_file in files:
            filename = uploaded_file.filename or "unnamed.pdf"

            if not filename.lower().endswith(".pdf"):
                return f"Invalid file type: {filename}", 400

            data = uploaded_file.read(MAX_FILE_SIZE + 1)

            if len(data) > MAX_FILE_SIZE:
                return f"File exceeds the 200 MB limit: {filename}", 400

            if not data.startswith(b"%PDF-"):
                return f"This does not appear to be a valid PDF: {filename}", 400

            reader = PdfReader(BytesIO(data), strict=False)

            if reader.is_encrypted:
                try:
                    decrypted = reader.decrypt("")
                except Exception:
                    decrypted = 0

                if not decrypted:
                    return (
                        f"Password-protected PDF: {filename}. "
                        "Please unlock it before merging."
                    ), 400

            for page in reader.pages:
                writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        output.seek(0)

        return send_file(
            output,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="Merged_PDF.pdf"
        )

    except Exception as error:
        return f"Could not merge PDFs: {error}", 400


if __name__ == "__main__":
    print("\\nPDF Merger started.")
    print("Open http://127.0.0.1:5000 in your browser.")
    print("Press CTRL+C to stop the application.\\n")

    app.run(host="127.0.0.1", port=5000, debug=False)
