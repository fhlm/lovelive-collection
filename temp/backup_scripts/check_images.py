import json
import os
import re
import sys

html_path = r'D:\Program\workspace\lovelive-collection\index.html'
base_dir = r'D:\Program\workspace\lovelive-collection'

# 读取 HTML 文件
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 提取 DATA 数组
pattern = r'const DATA = (\[.*?\]);'
match = re.search(pattern, content, re.DOTALL)
if not match:
    print('Could not find DATA array in HTML')
    sys.exit(1)

data_str = match.group(1)
# 尝试解析 JSON
try:
    data = json.loads(data_str)
except json.JSONDecodeError as e:
    print(f'JSON decode error: {e}')
    # 尝试修复常见问题：尾逗号
    data_str_fixed = re.sub(r',\s*]', ']', data_str)
    data_str_fixed = re.sub(r',\s*}', '}', data_str_fixed)
    try:
        data = json.loads(data_str_fixed)
    except json.JSONDecodeError as e2:
        print(f'Fixed JSON decode error: {e2}')
        sys.exit(1)

print(f'Total items in DATA: {len(data)}')

# 统计每个系列的条目数
series_count = {}
for item in data:
    series = item.get('series', 'Unknown')
    series_count[series] = series_count.get(series, 0) + 1
print('Series counts:')
for series, count in sorted(series_count.items()):
    print(f'  {series}: {count}')

# 检查图片文件是否存在
missing = []
invalid_path = []
for item in data:
    img_path = item.get('img', '')
    if not img_path:
        invalid_path.append(item)
        continue
    full_path = os.path.join(base_dir, img_path)
    if not os.path.exists(full_path):
        missing.append((item, full_path))

print(f'\nMissing image files: {len(missing)}')
if missing:
    print('First 10 missing:')
    for item, path in missing[:10]:
        print(f'  ID: {item.get("id")}, char: {item.get("char")}, img: {item.get("img")}')
        print(f'    Full path: {path}')

# 检查 thumbs 目录中的文件是否都被引用
thumbs_dir = os.path.join(base_dir, 'thumbs')
referenced_files = set()
for item in data:
    img_path = item.get('img', '')
    if img_path:
        # 规范化路径
        norm_path = os.path.normpath(img_path)
        referenced_files.add(norm_path)

# 收集所有 webp 文件
all_files = []
for root, dirs, files in os.walk(thumbs_dir):
    for file in files:
        if file.lower().endswith('.webp'):
            rel_path = os.path.relpath(os.path.join(root, file), base_dir)
            norm_path = os.path.normpath(rel_path)
            all_files.append(norm_path)

unreferenced = [f for f in all_files if f not in referenced_files]
print(f'\nTotal .webp files in thumbs: {len(all_files)}')
print(f'Referenced files: {len(referenced_files)}')
print(f'Unreferenced files: {len(unreferenced)}')
if unreferenced:
    print('First 10 unreferenced:')
    for f in unreferenced[:10]:
        print(f'  {f}')

# 检查文件名中的角色名是否与 DATA 中的 char 匹配（简单检查）
mismatched = []
for item in data:
    img_path = item.get('img', '')
    if not img_path:
        continue
    filename = os.path.basename(img_path)
    char = item.get('char', '')
    char_ja = item.get('charJa', '')
    # 检查文件名是否包含角色名（中文或日文）
    if char and char not in filename and char_ja and char_ja not in filename:
        mismatched.append((item, filename))

print(f'\nFilename-character mismatch (simple check): {len(mismatched)}')
if mismatched:
    print('First 10 mismatched:')
    for item, filename in mismatched[:10]:
        print(f'  ID: {item.get("id")}, char: {item.get("char")}, charJa: {item.get("charJa")}, filename: {filename}')