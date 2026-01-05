import json
import pandas as pd
from datetime import datetime
import glob
import os

# =============================
# 明确数据目录（关键）
# =============================
DATA_DIR = r"E:\spider"
os.chdir(DATA_DIR)
print("当前工作目录：", os.getcwd())

# =============================
# 1   获取原始文件列表
# =============================
files = glob.glob("*.info.json")
print(f"找到 {len(files)} 个 info.json 文件")

if len(files) == 0:
    raise RuntimeError("未找到任何 info.json 文件，请检查目录是否正确")

# =============================
# 2   定义分析口径
# =============================
cutoff_date = datetime(2024, 1, 1)
print("筛选条件：upload_date >= 2024-01-01")

rows = []

# =============================
#3 数据读取 + 筛选
# =============================
for f in files:
    try:
        with open(f, "r", encoding="utf-8") as file:
            data = json.load(file)

        upload_date = data.get("upload_date")
        if not upload_date:
            continue

        date = datetime.strptime(upload_date, "%Y%m%d")

        if date >= cutoff_date:
            rows.append({
                "video_id": data.get("id"),
                "title": data.get("title"),
                "upload_date": date.strftime("%Y-%m-%d"),
                "view_count": data.get("view_count", 0),
                "like_count": data.get("like_count", 0),
                "comment_count": data.get("comment_count", 0),
                "duration": data.get("duration", 0),
            })

    except Exception as e:
        print(f"处理文件 {f} 时出错：{e}")

# =============================
#4 输出结果
# =============================
df = pd.DataFrame(rows)

print("筛选完成 ✅")
print(f"最终保留视频数：{len(df)}")

OUTPUT_FILE = "mkbhd_last_1y.csv"
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("结果已保存到：", os.path.join(DATA_DIR, OUTPUT_FILE))
