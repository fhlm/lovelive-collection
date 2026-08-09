# lovelive-collection 项目长期记忆

## 项目基本信息

- **项目名称**：Love Live! 系列趴趴图鉴（Love Live! Nui Collection Checker）
- **用途**：Love Live! 全系列趴趴收藏进度追踪工具。
- **主要功能**：收藏管理、搜索筛选、中日文切换、移动端适配。
- **技术栈**：单文件 HTML（内联 CSS/JS/数据），无外部依赖。
- **数据来源**：官网新闻、公开信息、个人 Excel 图鉴。
- **部署方式**：GitHub Pages（https://fhlm.github.io/lovelive-collection/）。

## 文件结构

- `index.html`：主页面，包含所有逻辑和数据。
- `thumbs/`：缩略图目录，按系列分子文件夹（Aqours、Liella!、μ's、いきづらい部、莲之空、虹咲学园）。
- `items.json`：数据文件（可能未直接用于页面，但可作为数据源）。
- `lovelive趴趴图鉴26.8.7.xlsx`：原始 Excel 图鉴文件。

## 开发注意事项

- HTML 文件较大（约 0.4MB），修改时需谨慎。
- 数据内联在 HTML 中，如需更新数据，需找到相应数据结构进行修改。
- 缩略图路径格式：`thumbs/{系列}/{款式}.webp`。
- 收藏进度保存在浏览器 localStorage 中。

## 用户偏好

- 项目由用户（绯幻乱漫）创建，用于个人收藏管理。
- 可能需要定期更新数据（新商品发售时）。