# 高度选择



# 背景选择
# 打乱，选择前100张原始图片
# crop: 
    # 位置随机，但不能overlap到目标框
    # 尺度随机，高度和前100张text目标高度一致，宽度根据fontsize和期待文本的长度决定，达到贴合的状态
    # 次数，每张图片10000次

# 字体选择
# google font

# 文本选择
# 长度：1~10
# 内容：随机[0~9]


# 渲染
#参考原始脚本

# 保存
## 保存图片
## 保存txt

# Zilla Slab Highlight regular


def check_overlap(poly1, poly2):
    """
    判断两个四边形是否重叠
    poly1/poly2: 四边形顶点坐标列表，格式为 [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
    """
    # 创建多边形对象
    polygon1 = Polygon(poly1)
    polygon2 = Polygon(poly2)
    
    # 检查是否有交集（包括边重叠或包含）
    return polygon1.intersects(polygon2)
    

import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
height_img_root = r""
font_path = r""

height_list = []
img_path_list = random.shuffle(os.listdir(height_img_root))
for img_path in os.listdir(img_path_list):
    img = cv2.imread(img_path)
    h_img, w_img, _ = img.shape
    height_list.append(h_img)

src_img_path = r""
src_ann_path = r""
img_files = os.listdir(src_img_path)
img_files = random.shuffle(img_files)[:100]  # 打乱，并选择前100张图片

for idx, img_file in enumerate(img_files):
    name_without_ext, ext = os.splitext(img_file)
    ann_path = os.path.join(src_ann_path, name_without_ext + ".txt")
    img_path = os.path.join(src_img_path, img_file)
    
    
    coors_list = []
    img = Image.open(img_path)
    w_img, h_img = img.size
    
    with open(ann_path, "r") as fr:
        lines = fr.readlines()
    for line in lines:
        line = line.rstrip('\n')
        s_res = line.split(" ")
        label = s_res[0]
        coors_normalized = np.array([float(x) for x in s_res[1:]])  # 将普通List转变为np.ndarray，方便使用一些slice操作
        coors_list.append(coors_normalized)
    
    
    slice_height = np.random.choice(height_list)
    length = random.randint(1, 10)
    # 生成每一位数字（允许前导零）
    random_number = ''.join(str(random.randint(0, 9)) for _ in range(length))
    
    # 计算合适字体大小
    temp_size = 32  # 临时字号，越大计算越精确
    font_temp = ImageFont.truetype("ZillaSlabHighlight-Regular.ttf", temp_size)
    ascent, descent = font_temp.getmetrics()
    total_height_temp = ascent + descent
    # 调整字号使总高度等于图片高度
    final_size = int(height * temp_size / total_height_temp)    
    font = ImageFont.truetype("ZillaSlabHighlight-Regular.ttf", size)

    text_width = font.getlength(random_number)
    text_height = ascent + descent
    
    crop_width = text_width + 5
    crop_height = crop_height + 5
    
    h_start = np.random.choice(h_img)
    w_start = np.random.choice(w_img)
    
    background_box = np.array([w_start, h_start, w_start + crop_width -1, h_start, w_start + crop_width -1, h_start + crop_height - 1, w_start, h_start + crop_height - 1]).reshape(-1, 2)
    
    overlap = False
    for coors in coors_list:
        if check_overlap(background_box, coors):
            overlap = True
    
    if overlap == True:
        continue
    else:
        # 背景可以使用，进行渲染和数据的生成
        draw = ImageDraw.Draw(img)
        
        # Calculate position
        bbox = font.getbbox(text)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (self.size[0] - text_w) / 2
        y = (self.size[1] - text_h) / 2
        # Draw text
        draw.text((x, y), text, fill=(211, 211, 211), font=font)
        img.save(f"{idx}_{text}.jpg")

    
    