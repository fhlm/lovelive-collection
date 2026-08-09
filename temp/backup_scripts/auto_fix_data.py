import json
import os
import re
import sys
import shutil
from collections import defaultdict

base_dir = r'D:\Program\workspace\lovelive-collection'
html_path = os.path.join(base_dir, 'index.html')
thumb_index_path = os.path.join(base_dir, 'temp', 'thumb_index.json')
backup_dir = os.path.join(base_dir, 'temp', 'backup')
os.makedirs(backup_dir, exist_ok=True)

# 备份原始文件
backup_path = os.path.join(backup_dir, 'index.html.backup')
shutil.copy2(html_path, backup_path)
print(f'Backed up original HTML to {backup_path}')

# 读取 thumb_index
with open(thumb_index_path, 'r', encoding='utf-8') as f:
    thumb_index = json.load(f)

# 构建精确查找字典：(series, character, size, kind) -> 条目列表
thumb_dict精确 = {}
# 构建模糊查找字典：(series, character, size) -> 条目列表
thumb_dict模糊 = {}
for item in thumb_index:
    key精确 = (item['series'], item['character'], item['size'], item['kind'])
    thumb_dict精确.setdefault(key精确, []).append(item)
    key模糊 = (item['series'], item['character'], item['size'])
    thumb_dict模糊.setdefault(key模糊, []).append(item)

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

# 统计修正
fixed精确 = 0
fixed模糊 = 0
no_fix = 0
changes = []

for item in data:
    img_path = item.get('img', '')
    series = item.get('series', '')
    char = item.get('char', '')
    size = item.get('size', '')
    kind = item.get('type', '')
    
    # 提取当前文件名
    current_filename = os.path.basename(img_path) if img_path else ''
    
    # 精确匹配
    key精确 = (series, char, size, kind)
    matches精确 = thumb_dict精确.get(key精确, [])
    
    if matches精确:
        # 选择第一个匹配（或没有 _2 后缀的）
        best = matches精确[0]
        for m in matches精确:
            if not m['variant']:  # 没有 _2 后缀
                best = m
                break
        new_path = best['path']
        new_filename = best['filename']
        if new_filename != current_filename:
            item['img'] = new_path
            fixed精确 += 1
            changes.append({
                'id': item.get('id'),
                'old': img_path,
                'new': new_path,
                'reason': 'exact match'
            })
            continue
    
    # 模糊匹配
    key模糊 = (series, char, size)
    matches模糊 = thumb_dict模糊.get(key模糊, [])
    
    if matches模糊:
        # 选择第一个匹配
        best = matches模糊[0]
        for m in matches模糊:
            if not m['variant']:
                best = m
                break
        new_path = best['path']
        new_filename = best['filename']
        if new_filename != current_filename:
            item['img'] = new_path
            fixed模糊 += 1
            changes.append({
                'id': item.get('id'),
                'old': img_path,
                'new': new_path,
                'reason': 'fuzzy match'
            })
            continue
    
    no_fix += 1

print(f'\nFixes applied:')
print(f'  Exact matches: {fixed精确}')
print(f'  Fuzzy matches: {fixed模糊}')
print(f'  No fix needed: {no_fix}')

# 保存修正日志
log_path = os.path.join(base_dir, 'temp', 'fix_log.json')
with open(log_path, 'w', encoding='utf-8') as f:
    json.dump(changes, f, ensure_ascii=False, indent=2)
print(f'Saved fix log to {log_path}')

# 生成新的 DATA 字符串
new_data_str = 'const DATA = ' + json.dumps(data, ensure_ascii=False) + ';'

# 替换原始内容
new_content = content.replace(match.group(0), new_data_str)

# 写入文件
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print(f'Updated HTML file: {html_path}')

# 验证修改
print('\nVerification:')
for change in changes[:10]:
    print(f'  {change["id"]}: {change["old"]} -> {change["new"]} ({change["reason"]})')