import json
import os
import re
import sys

base_dir = r'D:\Program\workspace\lovelive-collection'
html_path = os.path.join(base_dir, 'index.html')
thumb_index_path = os.path.join(base_dir, 'temp', 'thumb_index.json')

# 读取 thumb_index
with open(thumb_index_path, 'r', encoding='utf-8') as f:
    thumb_index = json.load(f)

# 构建查找字典：以 (series, character, size) 为键，值为条目列表
thumb_dict = {}
for item in thumb_index:
    key = (item['series'], item['character'], item['size'])
    thumb_dict.setdefault(key, []).append(item)

# 从 index.html 提取 DATA
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'const DATA = (\[.*?\]);'
match = re.search(pattern, content, re.DOTALL)
if not match:
    print('Could not find DATA array in HTML')
    sys.exit(1)

data_str = match.group(1)
try:
    data = json.loads(data_str)
except json.JSONDecodeError as e:
    print(f'JSON decode error: {e}')
    sys.exit(1)

print(f'Total DATA items: {len(data)}')

# 对比
mismatched = []
missing_thumb = []
multiple_matches = []

for item in data:
    img_path = item.get('img', '')
    series = item.get('series', '')
    char = item.get('char', '')
    size = item.get('size', '')
    kind = item.get('type', '')
    
    # 从 img_path 提取文件名
    filename = os.path.basename(img_path) if img_path else ''
    
    # 在 thumb_dict 中查找
    key = (series, char, size)
    matches = thumb_dict.get(key, [])
    
    if not matches:
        # 尝试用日文角色名
        char_ja = item.get('charJa', '')
        # 但 thumb_index 中只有中文角色名，所以可能找不到
        missing_thumb.append(item)
        continue
    
    # 检查是否有匹配的文件名
    matched = False
    for m in matches:
        if m['filename'] == filename:
            matched = True
            break
    if not matched:
        # 文件名不匹配，但可能有其他匹配
        mismatched.append((item, matches))
    
    if len(matches) > 1:
        multiple_matches.append((item, matches))

print(f'\nMissing thumb entries (no match in thumb_index): {len(missing_thumb)}')
print(f'Filename mismatch (but has matches): {len(mismatched)}')
print(f'Multiple matches: {len(multiple_matches)}')

# 保存详细报告
report = {
    'missing_thumb': missing_thumb,
    'mismatched': [{'item': item, 'matches': matches} for item, matches in mismatched],
    'multiple_matches': [{'item': item, 'matches': matches} for item, matches in multiple_matches]
}
report_path = os.path.join(base_dir, 'temp', 'comparison_report.json')
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f'\nSaved detailed report to {report_path}')

# 打印一些示例
print('\nSample missing_thumb:')
for item in missing_thumb[:5]:
    print(f'  ID: {item.get("id")}, char: {item.get("char")}, size: {item.get("size")}, img: {item.get("img")}')

print('\nSample mismatched:')
for item, matches in mismatched[:5]:
    print(f'  ID: {item.get("id")}, char: {item.get("char")}, size: {item.get("size")}, img: {item.get("img")}')
    print(f'    Possible matches: {[m["filename"] for m in matches]}')