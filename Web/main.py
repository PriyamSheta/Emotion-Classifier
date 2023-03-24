from flask import send_from_directory
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import render_template
from url_utils import get_base_url
import requests, json, os

port = 12345
base_url = get_base_url(port)
if base_url == '/':
  app = Flask(__name__)
else:
  app = Flask(__name__, static_url_path=base_url + 'static')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024


def allowed_file(filename):
  return '.' in filename and \
         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route(f'{base_url}', methods=['GET', 'POST'])
def home():
  if request.method == 'POST':
    # check if the post request has the file part
    if 'file' not in request.files:
      flash('No file part')
      return redirect(request.url)

    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
      flash('No selected file')
      return redirect(request.url)

    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      return redirect(url_for('uploaded_file', filename=filename))

  return render_template('home.html')


@app.route(f'{base_url}/uploads/<filename>')
def uploaded_file(filename):
  here = os.getcwd()
  image_path = os.path.join(here, app.config['UPLOAD_FOLDER'], filename)

  API_URL = "https://api-inference.huggingface.co/models/PriyamSheta/EmotionClassModel"
  headers = {"Authorization": "Bearer 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"}

  def query(image_path):
    with open(image_path, "rb") as f:
      data = f.read()
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

  output = query(image_path)
  print(output)
  return render_template('results.html', data=output)


@app.route(f'{base_url}/uploads/<path:filename>')
def files(filename):
  return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
  # IMPORTANT: change url to the site where you are editing this file.
  website_url = 'google'
  print(f'Try to open\n\n    https://{website_url}' + base_url + '\n\n')
  app.run(host='0.0.0.0', port=port, debug=True)
