from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
CLIP_DIR = os.getenv('CLIP_DIR')
IMG_DIR = os.getenv('IMG_DIR').split(",")