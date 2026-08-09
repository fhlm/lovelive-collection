import os
import re
import json
from collections import defaultdict

base_dir = r'D:\Program\workspace\lovelive-collection'
thumbs_dir = os.path.join(base_dir, 'thumbs')

# 扫描 thumbs 目录
thumb_index = []
for root, dirs, files in os.walk(thumbs_dir):
    for file in files:
        if file.lower().endswith('.webp'):
            rel_path = os.path.relpath(os.path.join(root, file), base_dir)
            # 解析路径：thumbs/{series}/{kind}/{filename}.webp
            parts = rel_path.split(os.sep)
            if len(parts) >= 4:
                series = parts[1]
                kind = parts[2]
                filename = parts[3]
                # 解析文件名：{character}_{size}.webp 或 {character}_{size}_2.webp
                match = re.match(r'^(.+?)_(.+?)(?:_(\d+))?\.webp$', filename)
                if match:
                    character = match.group(1)
                    size = match.group(2)
                    variant = match.group(3)  # 可能为 None 或 '2'
                    thumb_index.append({
                        'series': series,
                        'kind': kind,
                        'character': character,
                        'size': size,
                        'variant': variant,
                        'filename': filename,
                        'path': rel_path
                    })

print(f'Total thumb files indexed: {len(thumb_index)}')

# 统计每个系列的文件数
series_counts = defaultdict(int)
for item in thumb_index:
    series_counts[item['series']] += 1
print('Thumb counts by series:')
for series, count in sorted(series_counts.items()):
    print(f'  {series}: {count}')

# 保存索引到 JSON
output_file = os.path.join(base_dir, 'temp', 'thumb_index.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(thumb_index, f, ensure_ascii=False, indent=2)
print(f'Saved thumb index to {output_file}')

# 打印一些示例
print('\nSample entries:')
for item in thumb_index[:10]:
    print(f'  {item["series"]}/{item["kind"]}/{item["character"]}_{item["size"]}.webp -> {item["path"]}')