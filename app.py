#clip img search project
from flask import Flask,request, redirect, url_for, render_template, jsonify, session
from clip_module import search_img, get_embedding_by_img, get_embedding_by_text
from PIL import Image
from io import BytesIO
from utils import PIL_to_b64
from config import IMG_DIR

app = Flask(__name__)
app.secret_key = 'clip'

@app.route("/")
def home():
    img_paths = session.get('img_paths')
    if img_paths:
        img_paths = img_paths.split(',')

    img_base64s = [PIL_to_b64(img_path) for img_path in img_paths]

    return render_template('index.html',img_base64s = img_base64s)

@app.route("/search_text")
def search_text():
    img_paths = session.get('img_paths')
    if img_paths:
        img_paths = img_paths.split(',')

    img_base64s = [PIL_to_b64(img_path) for img_path in img_paths]

    return render_template('search_text.html',img_base64s = img_base64s)

@app.route('/search_by_img', methods=['POST'])
def search_by_img():
    image_to_search = request.files.getlist('image')
    num = int(request.form.get("num"))
    img_bytes = image_to_search[0].read()
    img = Image.open(BytesIO(img_bytes))
    
    embedding = get_embedding_by_img(img)
    img_paths = search_img(embedding,IMG_DIR,num)
    print(img_paths)
    session['img_paths'] = ','.join(img_paths)
    return redirect(url_for('home'))

@app.route('/search_by_text', methods=['POST'])
def search_by_text():
    text = request.form['texts']
    num = int(request.form.get("num"))
    
    embedding = get_embedding_by_text(text)
    img_paths = search_img(embedding,IMG_DIR,num)
    print(img_paths)
    session['img_paths'] = ','.join(img_paths)
    return redirect(url_for('search_text'))

@app.route('/import')
def import_page():
    return render_template('import.html')

@app.route('/import_img', methods=['POST'])
def import_img():
    folder_path = request.form.get('folderPath')
    print(folder_path)
    if folder_path:
        return jsonify({'message': 'Folder path received', 'folderPath': folder_path})
    else:
        return jsonify({'message': 'No folder path received'}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)