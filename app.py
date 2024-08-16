#clip img search project
from flask import Flask,request, redirect, url_for, render_template, jsonify, session
from clip_module import search_img, get_embedding_by_img, get_embedding_by_text, save_to_vector_database
from PIL import Image
from io import BytesIO
from utils import PIL_to_b64
from config import IMG_DIR

app = Flask(__name__)
app.secret_key = 'clip'

@app.route("/")
def home():
    img_paths = session.get('img_paths', [])
    if img_paths:
        img_paths = img_paths.split(',')

    img_base64s = [PIL_to_b64(img_path) for img_path in img_paths]

    return render_template('index.html',img_base64s = img_base64s)

@app.route("/search_text")
def search_text():
    img_paths = session.get('img_paths', [])
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

@app.route('/import_page')
def import_page():
    return render_template('import_page.html')

@app.route('/import_img', methods=['POST'])
def import_img():
    folder_path = request.form.get('folderPath')
    print(folder_path)
    save_to_vector_database(folder_path)
    addtoenv(folder_path)
    return redirect(url_for('import_page'))

def addtoenv(folder_path):
    global IMG_DIR
    IMG_DIR.append(folder_path)
    print(IMG_DIR)

    print("setting config...")
        # 设置参数
    with open(".env", 'r', encoding="utf-8") as file:
        script_content = file.readlines()

        # 遍历文件内容,并修改需要更改的参数
    for i, line in enumerate(script_content):
        if line.startswith('IMG_DIR='):
            str = ","
            script_content[i] = f'IMG_DIR={str.join(IMG_DIR)}'
            break
        # 将修改后的内容写回文件
    with open(".env", 'w', encoding="utf-8") as file:
        file.writelines(script_content)
        print("setting config finished")

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)