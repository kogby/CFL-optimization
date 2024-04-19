# 添加相對路徑到 sys.path
import sys
import os
import yaml
sys.path.append('../')  
from path_config import INSTANCES_DIR

def load_specific_yaml(filename):
    """
    加載指定的 YAML 檔案。
    
    Parameters:
    filename (str): 在 instances 資料夾中的 YAML 檔案名。
    
    Returns:
    dict: YAML 檔案內容。
    """
    file_path = os.path.join(INSTANCES_DIR, filename)
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data