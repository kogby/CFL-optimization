import random
import yaml
import os
import sys

sys.path.append("../")
import utility as util
import numpy as np

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
V : Attractiveness yield of an unit of resource k allocated to facility j, Dim : (j, k)
H : Max demand for customer i, Dim : (i)
D : Distance between customer i and facility j , Dim : (i, j)
D_comp : Distance between customer i and competitor l, Dim : (i, l)
F : Fixed cost for building facility j, Dim : (j)
C : Cost per unit of extra attractiveness at facility j, Dim : (j)
B : Cost of allocating a unit of resource k to facility j, Dim : (j, k)
A_comp : The attractiveness level of competitor l, Dim: (l)
===============================
"""

loc_nums = [5, 25, 50]
opponent_nums = [5, 25, 50]
dist_formulas = ["euclidean", "manhattan"]
cus_gen_distribution = ["uniform", "normal"]
resource_nums = [1, 5, 10]
resource_benefit = []

ITERATION = 10
MAP_SIZE = 100
CUSTOMER_NUM = 5  # 客戶
FACILITY_NUM = 5  # 設廠地點
RESOURCE_NUM = 2  # 可分配資源
OPPONENT_NUM = 2  # 對手

for i in range(ITERATION):
    customers = util.create_points(CUSTOMER_NUM, MAP_SIZE)
    locations = util.create_points(FACILITY_NUM, MAP_SIZE)
    locations_oppo = util.create_points(OPPONENT_NUM, MAP_SIZE)

    U_L = [random.randint(5, 15) for _ in range(FACILITY_NUM)]
    U_T = [random.randint(5, 15) for _ in range(RESOURCE_NUM)]
    U_LT = [
        [random.randint(1, 5) for _ in range(RESOURCE_NUM)] for _ in range(FACILITY_NUM)
    ]
    F = [random.randint(1, 10) for _ in range(FACILITY_NUM)]
    C = [random.uniform(0.00005, 0.0003) for _ in range(FACILITY_NUM)]
    H = [random.randint(200, 4000) for _ in range(CUSTOMER_NUM)]
    D = util.dist_list_generator(customers, locations)
    D_comp = util.dist_list_generator(customers, locations_oppo)
    V = np.random.randint(10000, 500000, size=(FACILITY_NUM, RESOURCE_NUM)).tolist()
    B = np.random.randint(1, 5, size=(FACILITY_NUM, RESOURCE_NUM)).tolist()
    A_comp = [random.randint(1000, 15000) for _ in range(OPPONENT_NUM)]

    config = {
        "A_EX_bound": 1000000,  # bathroom limit
        "i_amount": CUSTOMER_NUM,
        "j_amount": FACILITY_NUM,
        "k_amount": RESOURCE_NUM,
        "l_amount": OPPONENT_NUM,
        "U_LT": U_LT,
        "U_T": U_T,
        "U_L": U_L,
        "V": V,
        "H": H,
        "D": D.tolist(),
        "D_comp": D_comp.tolist(),
        "A_opponent_bar": A_comp,
        "F": F,
        "C": C,
        "B": B,
    }

    # Write data to YAML file
    # current_time = datetime.datetime.now()
    # time_str = current_time.strftime("%m-%d_%H-%M")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.join(script_dir, "Instances")
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path, f"instance_F_{i+1}.yaml")

    # 寫入 yaml 檔案
    with open(file_path, "w") as yaml_file:
        yaml.dump(config, yaml_file, default_flow_style=False)
    print("Data saved to", file_path)
