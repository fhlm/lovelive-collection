import json
import os
import re
import sys
import shutil
from collections import defaultdict

base_dir = r'D:\Program\workspace\lovelive-collection'
html_path = os.path.join(base_dir, 'index.html')
excel_mapping_path = os.path.join(base_dir, 'temp', 'excel_mapping_v2.json')
thumb_index_path = os.path.join(base_dir, 'temp', 'thumb_index.json')
backup_dir = os.path.join(base_dir, 'temp', 'backup')
os.makedirs(backup_dir, exist_ok=True)

# 备份原始文件
backup_path = os.path.join(backup_dir, 'index.html.backup.v2')
shutil.copy2(html_path, backup_path)
print(f'Backed up original HTML to {backup_path}')

# 读取 Excel 映射
with open(excel_mapping_path, 'r', encoding='utf-8') as f:
    excel_mappings = json.load(f)
print(f'Loaded {len(excel_mappings)} Excel mappings')

# 读取 thumb_index
with open(thumb_index_path, 'r', encoding='utf-8') as f:
    thumb_index = json.load(f)
print(f'Loaded {len(thumb_index)} thumb entries')

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

# 构建日文角色名到中文角色名的映射
char_ja_to_cn = {}
for item in data:
    char_ja = item.get('charJa', '')
    char_cn = item.get('char', '')
    if char_ja and char_cn:
        char_ja_to_cn[char_ja] = char_cn
print(f'Character mapping: {len(char_ja_to_cn)} entries')

# 构建 thumb_index 查找字典： (series, character_cn, size, kind) -> 条目列表
thumb_dict = {}
for item in thumb_index:
    # thumb_index 中的 character 是中文
    key = (item['series'], item['character'], item['size'], item['kind'])
    thumb_dict.setdefault(key, []).append(item)

# 构建 Excel 映射到文件路径的映射
excel_to_file = {}
missing_in_thumb = []
for excel_map in excel_mappings:
    series = excel_map['series']
    char_ja = excel_map['character_ja']
    size = excel_map['size']
    kind = excel_map['kind']
    
    # 转换角色名为中文
    char_cn = char_ja_to_cn.get(char_ja, char_ja)  # 如果找不到，使用日文名
    
    # 在 thumb_dict 中查找
    key = (series, char_cn, size, kind)
    matches = thumb_dict.get(key, [])
    
    if matches:
        # 选择第一个匹配（或没有 _2 后缀的）
        best = matches[0]
        for m in matches:
            if not m['variant']:
                best = m
                break
        excel_to_file[excel_map] = best['path']
    else:
        missing_in_thumb.append(excel_map)

print(f'Excel mappings with file: {len(excel_to_file)}')
print(f'Excel mappings missing in thumb: {len(missing_in_thumb)}')

# 现在修正 DATA
fixed = 0
no_fix = 0
changes = []

for item in data:
    series = item.get('series', '')
    char_cn = item.get('char', '')
    size = item.get('size', '')
    kind = item.get('type', '')
    
    # 在 excel_to_file 中查找匹配
    # 需要遍历 excel_to_file，因为键是 excel_map 对象
    found = False
    for excel_map, file_path in excel_to_file.items():
        if (excel_map['series'] == series and
            char_ja_to_cn.get(excel_map['character_ja'], excel_map['character_ja']) == char_cn and
            excel_map['size'] == size and
            excel_map['kind'] == kind):
            # 找到匹配
            old_img = item.get('img', '')
            if old_img != file_path:
                item['img'] = file_path
                fixed += 1
                changes.append({
                    'id': item.get('id'),
                    'old': old_img,
                    'new': file_path,
                    'reason': 'Excel mapping match'
                })
            found = True
            break
    
    if not found:
        no_fix += 1

print(f'\nFixes applied: {fixed}')
print(f'No fix needed: {no_fix}')

# 保存修正日志
log_path = os.path.join(base_dir, 'temp', 'fix_log_v2.json')
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

# 检查未匹配的 Excel 映射
if missing_in_thumb:
    print(f'\nFirst 5 missing Excel mappings:')
    for excel_map in missing_in_thumb[:5]:
        print(f'  Series: {excel_map["series"]}, Character: {excel_map["character_ja"]}, '
              f'Size: {excel_map["size"]}, Kind: {excel_map["kind"]}')