"""This file is used to compare the obj percentage gap between algorithm and gurobi"""
import os
import yaml
import pandas as pd
import matplotlib.pyplot as plt


def extract_best_obj(result_path):
    with open(result_path, "r") as file:
        result_data = yaml.safe_load(file)
        best_obj = result_data.get("OBJ_value", None)
        return best_obj


def compare_obj(result_base_path_1, other_algo_df, instance_type):
    my_best_objs = []
    other_best_objs = other_algo_df["OBJ_value"].tolist()

    for i in range(1, 101):
        result_path_1 = os.path.join(
            result_base_path_1, instance_type, f"result_{instance_type}_{i}.yaml"
        )
        if os.path.exists(result_path_1):
            my_best_obj = extract_best_obj(result_path_1)
            if my_best_obj is not None:
                my_best_objs.append(my_best_obj)

    # Calculate the percentage difference
    percentage_diff = [
        (my / other * 100) if other != 0 else 100
        for my, other in zip(my_best_objs, other_best_objs)
    ]

    return percentage_diff


# Example usage
result_base_path_1 = os.path.join("Benchmark-Test", "OG_Model_0430", "result")
output_dir = "plots_greedyV1_vs_gurobi"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load the DataFrame containing results of the other algorithm
path = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(path, result_base_path_1)
other_algo_dfs = {
    "S": pd.read_excel(os.path.join(csv_path, "gurobi_S.xlsx")),
    "M": pd.read_excel(os.path.join(csv_path, "gurobi_M.xlsx")),
    "L": pd.read_excel(os.path.join(csv_path, "gurobi_L.xlsx")),
}

for instance_type in ["S", "M", "L"]:
    other_algo_df = other_algo_dfs[instance_type]
    percentage_diff = compare_obj(result_base_path_1, other_algo_df, instance_type)

    # Calculate the average percentage difference
    average_percentage_diff = sum(percentage_diff) / len(percentage_diff)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(
        range(1, len(percentage_diff) + 1), percentage_diff, marker="o", linestyle=""
    )  # marker without line
    plt.xlabel("Instance Index")
    plt.ylabel("(Greedy / Gurobi) % of Obj")
    plt.title(f"Percentage Difference of Best Obj for Instance Type {instance_type}")
    plt.grid(True)
    plt.axhline(y=100, color="k", linestyle="--")  # Add horizontal line at 100%
    plt.axhline(
        y=average_percentage_diff,
        color="r",
        linestyle="-",
        label=f"Average: {average_percentage_diff:.2f}%",
    )
    plt.legend()
    plt.savefig(os.path.join(output_dir, f"percentage_difference_{instance_type}.png"))
