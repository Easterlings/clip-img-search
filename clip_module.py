
# 用CLIP提取图像嵌入并将嵌入存储到矢量数据库Pinecone中
import os
# import pinecone
from transformers import CLIPModel, CLIPProcessor
from pathlib import Path
# 初始化 Pinecone 客户端
from pinecone import Pinecone
from PIL import Image
from config import PINECONE_API_KEY,PINECONE_INDEX_NAME,CLIP_DIR,IMG_DIR
from utils import strtob64,b64tostr
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# 加载 CLIP 模型和处理器
model_dir = Path(CLIP_DIR)
model = CLIPModel.from_pretrained(model_dir)
processor = CLIPProcessor.from_pretrained(model_dir)

def save_to_vector_database(input_dir):
    # 从一个文件夹递归遍历图像并提取嵌入到数据库
    print("==========================",input_dir,"==========================")
    for filename  in os.listdir(input_dir):
        item_path = os.path.join(input_dir, filename)
        if os.path.isdir(item_path):
            save_to_vector_database(item_path)
        else:
            if filename.endswith("720.jpg") or filename.endswith(".png"):
                # 加载图像
                image_path = os.path.join(input_dir, filename)
                img = Image.open(image_path)
                embedding = get_embedding_by_img(img)
                base64_file_name = strtob64(filename)
                # 将嵌入存储到 Pinecone 索引
                index.upsert([(base64_file_name, embedding)])
                print(filename)

def get_embedding_by_img(img):
    image = processor(images=img, return_tensors="pt").pixel_values
    output = model.get_image_features(image)
    embedding = output.tolist()
    return embedding[0]

def get_embedding_by_text(text):
    inputs = processor(text=text, return_tensors="pt", padding=True)
    text_features = model.get_text_features(**inputs)
    embedding = text_features.tolist()
    return embedding[0]

def search_img(embedding,folder_paths,num = 5):
    #从目录及其子目录中搜索当前图片最相似的num张图片，
    results = index.query(vector=embedding, top_k=num)

    print("Top 5 similar images:")
    for result in results["matches"]:
        print(f"ID: {b64tostr(result['id'])}, Score: {result['score']}")
    base64_img_names = [i['id'] for i in results["matches"]]
    image_names = [b64tostr(base64_img_name) for base64_img_name in base64_img_names]
    
    img_paths = []
    for folder_path in folder_paths:
        for image_name in image_names:
            img_path = search_imgname_in_folder(folder_path, image_name)
            if img_path:
                img_paths.append(img_path) 
    print(img_paths)
    return img_paths

def search_imgname_in_folder(folder_path, image_name):
    #从当前目录搜索image_name，返回完整路径
    image_path = os.path.join(folder_path, image_name)
    if os.path.exists(image_path):
        return image_path
    # 当前目录没找到时，考虑子目录
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            image_path = search_imgname_in_folder(item_path, image_name)
            if(image_path):
                return image_path
    return False


if __name__ == '__main__':
    # # 定义输入图像目录
    input_dirs = IMG_DIR
    for input_dir in input_dirs:
        save_to_vector_database(input_dir)
