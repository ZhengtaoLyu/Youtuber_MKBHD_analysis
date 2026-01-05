import pandas as pd
import numpy as np
import os

# =============================
# 0️⃣ 读取 CSV 文件（支持多编码 & Tab 分隔）
# =============================
DATA_FILE = r"E:\spider\mkbhd_last_1y.csv"

# 尝试读取文件，如果 utf-8 失败就用 gbk
encodings_to_try = ['utf-8', 'utf-8-sig', 'gbk', 'latin1']
for enc in encodings_to_try:
    try:
        df = pd.read_csv(DATA_FILE, encoding=enc, sep='\t')  # 指定 Tab 分隔
        print(f"✅ CSV 文件读取完成，使用编码：{enc}")
        break
    except UnicodeDecodeError:
        print(f"⚠️ 编码 {enc} 读取失败，尝试下一个编码...")
else:
    raise ValueError("❌ 所有常见编码读取失败，请确认 CSV 文件编码格式")

print(f"原始视频数量：{len(df)}")
print("列名：", df.columns.tolist())

# =============================
# 1️⃣ 数据清洗
# =============================
# 检查必要列是否存在
required_columns = ['video_id','upload_date','view_count','like_count','comment_count','title','duration']
missing_cols = [col for col in required_columns if col not in df.columns]
if missing_cols:
    raise ValueError(f"❌ 缺失必要列: {missing_cols}")

# 去重
df = df.drop_duplicates(subset='video_id')

# 日期转换
df['upload_date'] = pd.to_datetime(df['upload_date'], errors='coerce', format='%Y/%m/%d')
df = df.dropna(subset=['upload_date'])  # 删除无法解析的日期

# 筛选最近两年的数据（可选）
cutoff_date = pd.Timestamp('2024-01-01')
df = df[df['upload_date'] >= cutoff_date]
print(f"筛选后的视频数量：{len(df)}")

# 缺失值检查
print("缺失值统计：\n", df.isnull().sum())

# log 变换处理异常值（先填充缺失值为0）
df['view_count'] = df['view_count'].fillna(0)
df['like_count'] = df['like_count'].fillna(0)
df['comment_count'] = df['comment_count'].fillna(0)

df['view_count_log'] = np.log1p(df['view_count'])
df['like_count_log'] = np.log1p(df['like_count'])
df['comment_count_log'] = np.log1p(df['comment_count'])

# =============================
# 2️⃣ 特征工程
# =============================
df['engagement_rate'] = (df['like_count'] + df['comment_count']) / df['view_count'].replace(0,1)
df['title_length'] = df['title'].astype(str).str.len()
df['is_question'] = df['title'].astype(str).str.contains(r'？|\?', regex=True)
df['duration_min'] = df['duration'].fillna(0) / 60

# 时长分桶
bins = [0,5,10,15,20,25,30]
labels = ['0-5','5-10','10-15','15-20','20-25','25-30']
df['duration_bucket'] = pd.cut(df['duration_min'], bins=bins, labels=labels, right=False)

# 发布时间特征
df['publish_hour'] = df['upload_date'].dt.hour
df['publish_weekday'] = df['upload_date'].dt.dayofweek

# 标题关键词特征
df['has_number'] = df['title'].astype(str).str.contains(r'\d+')

# 相对指标
total_views = df['view_count'].sum() if df['view_count'].sum() > 0 else 1
total_engagements = (df['like_count'].sum() + df['comment_count'].sum()) if (df['like_count'].sum() + df['comment_count'].sum()) > 0 else 1
df['view_ratio'] = df['view_count'] / total_views
df['engagement_ratio'] = (df['like_count'] + df['comment_count']) / total_engagements

# 时长四分位
df['duration_quartile'] = pd.qcut(df['duration_min'], 4, labels=['Q1','Q2','Q3','Q4'])

# =============================
# 3️⃣ 保存特征 CSV
# =============================
OUTPUT_FILE = r"E:\spider\mkbhd_last_1y_features.csv"
df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
print("特征生成完成 ✅ CSV 已保存")
