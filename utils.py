from io import BytesIO
import base64
from PIL import Image

def PIL_to_b64(img_path):
    img = Image.open(img_path).convert("RGB")
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def b64tostr(str):
    # b64解码
    return base64.b64decode(str.encode('ascii')).decode('utf-8')

def strtob64(str):
    # b64编码
    return base64.b64encode(str.encode('utf-8')).decode('ascii')

if __name__ == '__main__':
    image_path = "C:/Users/Paul_Argery/Pictures/u=526150015,2408323338&fm=15&gp=0.jpg"
    print(PIL_to_b64(image_path))