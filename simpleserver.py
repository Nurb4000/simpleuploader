# simple_file_server.py
import os
from pathlib import Path
from flask import Flask, request, render_template_string, redirect, url_for, flash

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
UPLOAD_DIR = Path("uploads")          # where uploaded files will be stored
UPLOAD_DIR.mkdir(exist_ok=True)       # create the folder if it doesn’t exist
MAX_CONTENT_LENGTH = None  

# ----------------------------------------------------------------------
# Flask app setup
# ----------------------------------------------------------------------
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.secret_key = "dev-secret-key"   # needed for flashing messages (not used for auth)

# Simple HTML template – you can expand or replace it later
HTML_FORM = """
<!doctype html>
<title>Simple Upload Server</title>
<h2>Upload Files</h2>

{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul style="color:red;">
      {% for msg in messages %}
        <li>{{msg}}</li>
      {% endfor %}
    </ul>
  {% endif %}
{% endwith %}

<form method=post enctype=multipart/form-data>
  <input type=file name=file multiple>
  <input type=submit value=Upload>
</form>

<hr>
<h3>Uploaded files</h3>
<ul>
{% for f in files %}
  <li>{{f}}</li>
{% else %}
  <li>(none)</li>
{% endfor %}
</ul>
"""

# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Flask puts each uploaded file into request.files
        uploaded = request.files.getlist("file")
        if not uploaded:
            flash("No file selected.")
            return redirect(request.url)

        for file_obj in uploaded:
            # Skip empty uploads
            if file_obj.filename == "":
                continue

            # Secure the filename (avoid directory traversal)
            filename = os.path.basename(file_obj.filename)
            dest_path = UPLOAD_DIR / filename

            # Save the file (overwrites if same name exists)
            file_obj.save(dest_path)

        flash(f"Successfully uploaded {len(uploaded)} file(s).")
        return redirect(url_for("index"))

    # GET request – show the form + list of already‑uploaded files
    existing_files = sorted(p.name for p in UPLOAD_DIR.iterdir() if p.is_file())
    return render_template_string(HTML_FORM, files=existing_files)


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Run on all interfaces (0.0.0.0) so any machine on the LAN can reach it.
    # Port 5000 is Flask’s default; change if you need another.
    app.run(host="0.0.0.0", port=5000, debug=False)