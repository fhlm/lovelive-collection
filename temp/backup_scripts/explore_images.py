import openpyxl
import os

excel_path = r'D:\Program\workspace\lovelive-collection\lovelive趴趴图鉴26.8.7.xlsx'

try:
    wb = openpyxl.load_workbook(excel_path, read_only=False)
    
    # 只处理第一个 sheet 进行测试
    sheet_name = wb.sheetnames[0]
    ws = wb[sheet_name]
    print(f'Processing sheet: {sheet_name}')
    
    # 获取图片数量
    images = ws._images
    print(f'Total images: {len(images)}')
    
    # 检查第一个图片的属性
    if images:
        img = images[0]
        print(f'\nFirst image properties:')
        print(f'  Type: {type(img)}')
        print(f'  Width: {img.width}')
        print(f'  Height: {img.height}')
        
        # 检查 anchor 属性
        if hasattr(img, 'anchor'):
            anchor = img.anchor
            print(f'  Anchor type: {type(anchor)}')
            print(f'  Anchor attributes: {dir(anchor)}')
            
            # 检查 _from 和 _to
            if hasattr(anchor, '_from'):
                from_ = anchor._from
                print(f'  _from type: {type(from_)}')
                print(f'  _from attributes: {dir(from_)}')
                if hasattr(from_, 'row'):
                    print(f'  _from.row: {from_.row}')
                if hasattr(from_, 'col'):
                    print(f'  _from.col: {from_.col}')
                if hasattr(from_, 'rowOff'):
                    print(f'  _from.rowOff: {from_.rowOff}')
                if hasattr(from_, 'colOff'):
                    print(f'  _from.colOff: {from_.colOff}')
            
            if hasattr(anchor, '_to'):
                to_ = anchor._to
                print(f'  _to type: {type(to_)}')
                if hasattr(to_, 'row'):
                    print(f'  _to.row: {to_.row}')
                if hasattr(to_, 'col'):
                    print(f'  _to.col: {to_.col}')
                if hasattr(to_, 'rowOff'):
                    print(f'  _to.rowOff: {to_.rowOff}')
                if hasattr(to_, 'colOff'):
                    print(f'  _to.colOff: {to_.colOff}')
        
        # 检查是否有其他属性
        print(f'\nAll image attributes:')
        for attr in dir(img):
            if not attr.startswith('_'):
                try:
                    value = getattr(img, attr)
                    if not callable(value):
                        print(f'  {attr}: {value}')
                except:
                    pass
    
    wb.close()
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()