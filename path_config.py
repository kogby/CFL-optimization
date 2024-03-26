# 這個模塊用於定義整個專案中使用的配置數據和路徑。
# 它使得管理和更新這些信息更加集中和方便。
import os

# 使用__file__獲取當前文件的絕對路徑，並使用os.path.dirname獲取當前文件所在目錄的路徑。
# BASE_DIR代表了專案根目錄的路徑，方便後續與其他相對路徑結合使用。
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 使用os.path.join來保證路徑在不同作業系統上的兼容性。
# 那麼YAML_FILE_PATH將被設置為指向該文件的完整路徑。

INSTANCES_DIR = os.path.join(BASE_DIR, 'Instance', 'Instances')  # 不指定是哪個yaml檔案，交給要call的決定

# 你可以根據需要在這裡添加更多配置數據或路徑變數，並通過從其他Python文件導入此模塊來使用它們。
