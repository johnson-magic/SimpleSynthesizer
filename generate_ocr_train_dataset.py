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



    
import os
import json
import jsonlines
import tqdm
from utils.utils import Synthesizer

slice_root = r"../../autodl-tmp/direction_dataset/0/"
font_root = r"./font/BigShouldersInline.ttf" # # 2w * 2
# font_root = r"./font/WireOne-Regular.ttf"#  5w * 2
# font_root = r"./font/RubikMicrobe-Regular.ttf"  # 10w * 2
# font_root = r"./font/MartianMono-VariableFont_wdth,wght.ttf" #  20w * 2
background_root = r"../../autodl-tmp/project-ocr-202504/"
save_root = r"../../autodl-tmp/synthesis/text_recog/bigshouldersinline"
synthesizer = Synthesizer(slice_root, font_root, background_root, save_root)

sample_num = 40000
ann_infos = []
for i in tqdm.tqdm(range(sample_num)):
    ann_info = synthesizer()
    ann_infos.append(ann_info)
    
# with open(os.path.join(save_root, "textrecog_train.json"), "w") as outfile:
#     json.dump(ann_infos, outfile, ensure_ascii = False, indent = 4)

# with open(os.path.join(save_root, "textrecog_train.txt"), "w") as outfile:
#     # json.dump(ann_infos, outfile, ensure_ascii = False, indent = 4)
#     for filename, label in ann_infos:
#         outfile.writelines(f"{filename} {label}\n")

with jsonlines.open(os.path.join(save_root, "textrecog_train.jsonl"), 'w') as writer:
    writer.write_all(ann_infos)
    
    

    
    
