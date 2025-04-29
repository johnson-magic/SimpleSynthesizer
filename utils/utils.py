import os
import cv2
import time
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon

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


class Synthesizer(object):
    def __init__(self, slice_root: str, font_path: str, background_root: str, save_root: str):
        self.slice_root = slice_root
        self.height_candicates = self.height_candicates()
        
        self.background_root = background_root  # images和labels
        self.background_candicates, self.background_filters = self.background_candicates()  # 可能会占用较大的内存，几百张背景图片，应该还好，但速度会比较快
        
        self.font_path = font_path
        self.font = self.init_font()
        
        self.save_root = save_root
        # if not os.path.exists(os.path.join(self.save_root, "images")):
        #     os.mkdir(os.path.join(self.save_root, "images"))
        # if not os.path.exists(os.path.join(self.save_root, "labels")):
        #     os.mkdir(os.path.join(self.save_root, "labels"))
    
    def __call__(self):
        # 从随机选择一个slice的高度出发
        slice_height = np.random.choice(self.height_candicates)
        
        # 根据已经确定的slice_height，来计算合适字体大小
        self.font = self.adaptive_font(slice_height)
        ascent, descent = self.font.getmetrics()
        
        # 随机生成长度为[1~10], 内容为[0~9]之间的数字内容
        label = self.text_generate()
        
        
        text_width = self.font.getlength(label)
        text_height = ascent + descent

        crop_width = text_width  # + 3 * 2  # 稍稍的做一下扩展
        crop_height = text_height # + 3 * 2
        
        # 处理背景
        bg_id_choice = np.random.choice(len(self.background_candicates))
        img_bg, filter_bg = self.background_candicates[bg_id_choice], self.background_filters[bg_id_choice]
        w_img, h_img = img_bg.size
         
        h_start = np.random.choice(h_img)
        w_start = np.random.choice(w_img)
        background_box = [(w_start, h_start),
                          (w_start + crop_width -1, h_start),
                          (w_start + crop_width -1, h_start + crop_height - 1),
                          (w_start, h_start + crop_height - 1)]

        overlap = False
        left = 3 # 3次机会，
        for filter_bg_item in filter_bg:
            filter_bg_item = filter_bg_item.reshape(4, 2)
            filter_bg_item = [tuple(row) for row in filter_bg_item]
            if check_overlap(background_box, filter_bg_item):
                overlap = True
                break
        
        while overlap and left > 0:
            h_start = np.random.choice(h_img)
            w_start = np.random.choice(w_img)
            background_box = [(w_start, h_start),
                              (w_start + crop_width -1, h_start),
                              (w_start + crop_width -1, h_start + crop_height - 1),
                              (w_start, h_start + crop_height - 1)]

            overlap = False
            for filter_bg_item in filter_bg:
                filter_bg_item = filter_bg_item.reshape(4, 2)
                filter_bg_item = [tuple(row) for row in filter_bg_item]
                if check_overlap(background_box, filter_bg_item):
                    overlap = True
                    break
            
            left = left - 1

        if not overlap:  # 3次机会使用完毕，还是unvalid, 则放弃这次机会
            # 背景可以使用，进行渲染和数据的生成
            img_slice = img_bg.crop((w_start, h_start, w_start + crop_width -1, h_start + crop_height - 1))
            draw = ImageDraw.Draw(img_slice)

            # Calculate position
            bbox = self.font.getbbox(label)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (crop_width - text_w) / 2
            y = (crop_height - text_h) / 2
            # Draw text
            # draw.text((x, y), label, fill=(211, 211, 211), font=self.font)
            
            draw.text((x, y), label, fill="gray", font=self.font)
            
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            # img_slice.save(os.path.join(self.save_root, "images", f"{timestamp}_{label}.png"))
            img_slice.save(os.path.join(self.save_root, f"{timestamp}_{label}.png"))
            
            return {"filename": f"{timestamp}_{label}.png", "text": label}  # 以mmocr为例，后续组装统一保存为一个jsonl文件 
            # return (f"{timestamp}_{label}.png", label)
        else:
            return None
            # with open(os.path.join(self.save_root, "labels", f"{timestamp}_{label}.txt"), "w") as fw:
            #    fw.write(label)
            

    def height_candicates(self):
        """获得Synthesizer的height候选列表，后续的Synthesis在该列表中随机挑选
        """
        height_list = []
        img_path_list = os.listdir(self.slice_root)
        random.shuffle(img_path_list)  # in place
        for img_path in img_path_list:
            if not img_path.endswith((".bmp", ".jpg", ".png")):
                continue
            img = cv2.imread(os.path.join(self.slice_root, img_path))
            h_img, w_img, _ = img.shape
            height_list.append(h_img)
        return height_list
    
    
    def init_font(self):
        temp_size = 32  # 临时字号，越大计算越精确
        font_temp = ImageFont.truetype(self.font_path, temp_size)
        return font_temp
    
    
    def adaptive_font(self, height: int):
        """
        Args:
            height: int, height of slice
        """
        ascent, descent = self.font.getmetrics()
        total_height = ascent + descent
        
        # 调整字号使总高度等于图片高度
        adaptive_size = int(height * self.font.size / total_height)    
        adaptive_font = ImageFont.truetype(self.font_path, adaptive_size)
        return adaptive_font
    
    def text_generate(self):
        length = random.randint(1, 10)
        # 生成每一位数字（允许前导零）
        random_number = ''.join(str(random.randint(0, 9)) for _ in range(length))
        return random_number
    
    def background_candicates(self):
        img_root = os.path.join(self.background_root, "images")
        ann_root = os.path.join(self.background_root, "labels")
        
        background_candicates = []
        background_filters = []
        
        for idx, img_file in enumerate(os.listdir(img_root)):
            if not img_file.endswith((".bmp", ".jpg", ".png")):
                continue
            name_without_ext, ext = os.path.splitext(img_file)
            ann_path = os.path.join(ann_root, name_without_ext + ".txt")      
            img_path = os.path.join(img_root, img_file)
            
            coors_list = []
            img = Image.open(img_path).convert("RGB")
            w_img, h_img = img.size

            with open(ann_path, "r") as fr:
                lines = fr.readlines()
            for line in lines:
                line = line.rstrip('\n')
                s_res = line.split(" ")
                coors_normalized = np.array([float(x) for x in s_res[1:]])  # 将普通List转变为np.ndarray，方便使用一些slice操作
                coors_normalized[0::2] = coors_normalized[0::2] * w_img
                coors_normalized[1::2] = coors_normalized[1::2] * h_img
                
                coors_list.append(coors_normalized)
            
            coors_numpy = np.stack(coors_list, 0)
            
            background_candicates.append(img)
            background_filters.append(coors_numpy)
        
        return background_candicates, background_filters