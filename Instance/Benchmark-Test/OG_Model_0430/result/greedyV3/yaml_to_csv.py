import os
import yaml
import pandas as pd
import re

# 定義資料夾的絕對路徑
base_path = '/Users/wuhuayo/Desktop/CFL-optimization/Instance/Benchmark-Test/OG_Model_0430/result/greedyV3'
folders = ['L', 'M', 'S']

# 正則表達式提取文件名中的數字
pattern = re.compile(r'result_[A-Z]_(\d+).yaml')

for folder in folders:
    obj_values = []
    folder_path = os.path.join(base_path, folder)
    # 獲取資料夾中所有yaml檔案
    yaml_files = [f for f in os.listdir(folder_path) if f.endswith('.yaml')]
    
    for yaml_file in yaml_files:
        match = pattern.search(yaml_file)
        if match:
            index = int(match.group(1))
            with open(os.path.join(folder_path, yaml_file), 'r') as file:
                data = yaml.safe_load(file)
                obj_values.append({'Index': index, 'OBJ_value': data['OBJ_value']})
    
    # 按索引排序
    obj_values.sort(key=lambda x: x['Index'])
    
    # 將obj_values寫入CSV檔案
    df = pd.DataFrame(obj_values)
    csv_filename = os.path.join(base_path, f'{folder}_obj_values.csv')
    df.to_csv(csv_filename, index=False)
    print(f'Saved {csv_filename}')
