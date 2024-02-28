import random
import yaml

"""
Instance Parameters
===============================
Customer Location: I
Facility Location: J
Resource Type: K
Competitor Facility Location: L

U_LT : Max amount of resource k allowed to be allocated to facility j, Dim : (j, k)
U_T : Max allocation limit for resource k, Dim : (k)
U_L : Max capacity for facility j, Dim : (j)
V : Attractiveness yield of resource k allocated to facility j, Dim : (j, k)
H : Max demand for customer i, Dim : (i)
D : Distance between customer i and facility j , Dim : (i, j)
D_comp : Distance between customer i and competitor l, Dim : (i, l)
F : Fixed cost for building facility j, Dim : (j)
C : Cost per unit of extra attractiveness at facility j, Dim : (j)
B : Cost of allocating a unit of resource k to facility j, Dim : (j, k)
===============================
"""

MAP_SIZE = 100
CUSTOMER_NUM = 2  # 2個客戶
FACILITY_NUM = 3  # 三個設廠地點
RESOURCE_NUM = 2  # 兩種可分配資源（大車, 小車)

U_L = [random.randint(1, 10) for _ in range(FACILITY_NUM)]
U_T = [random.randint(3, 10) for _ in range(RESOURCE_NUM)]
config = {
    "M": 1000000,
    "lambda_G": 0.5,
    "i_amount": 2,
    "j_amount": 3,
    "k_amount": 2,
    "l_amount": 0,  # 對手數量
    "U_LT": [[3, 5], [3, 5], [3, 5]],
    "U_T": [5, 10],
    "U_L": U_L,
    "V": [[10, 2], [2, 1], [0, 2]],
    "H": [100, 50],
    "D": [[1, 1, 1], [1, 1, 1]],
    "D_comp": [],
    "A_opponent_bar": [],  # 對手吸引力
    "F": [0, 0, 0],
    "C": [1, 1, 1],
    "B": [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
}


# Write data to YAML file
file_path = "experiment_data.yaml"
with open(file_path, "w") as yaml_file:
    yaml.dump(config, yaml_file, default_flow_style=False)

print("Data saved to", file_path)
