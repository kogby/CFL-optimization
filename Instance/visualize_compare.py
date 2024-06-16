# """This file is used to compare the obj percentage gap between algorithm and gurobi"""
import os
import yaml
import pandas as pd
import matplotlib.pyplot as plt


def extract_best_obj(result_path):
    with open(result_path, "r") as file:
        result_data = yaml.safe_load(file)
        best_obj = result_data.get("OBJ_value", None)
        return best_obj


def compare_obj(result_base_paths, other_algo_df, instance_type):
    best_objs_list = []
    other_best_objs = other_algo_df["OBJ_value"].tolist()

    for result_base_path in result_base_paths:
        best_objs = []
        for i in range(1, 101):
            result_path = os.path.join(
                result_base_path, instance_type, f"result_{instance_type}_{i}.yaml"
            )
            if os.path.exists(result_path):
                best_obj = extract_best_obj(result_path)
                if best_obj is not None:
                    best_objs.append(best_obj)
        best_objs_list.append(best_objs)

    # Calculate the percentage differences for each result base path
    percentage_diffs = []
    for best_objs in best_objs_list:
        percentage_diff = [
            (my / other * 100) if other != 0 else 100
            for my, other in zip(best_objs, other_best_objs)
        ]
        percentage_diffs.append(percentage_diff)

    return percentage_diffs


# Example usage
current_dir = os.path.dirname(os.path.abspath(__file__))
result_base_path_1 = os.path.join(
    current_dir, "Benchmark-Test/OG_Model_0430/result/greedyV2"
)
result_base_path_2 = os.path.join(
    current_dir, "Benchmark-Test/OG_Model_0430/result/greedyV3"
)
output_dir = os.path.join(current_dir, "plots_greedyV3_vs_gurobi")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load the DataFrame containing results of the other algorithm
csv_path = os.path.join(current_dir, "Benchmark-Test/OG_Model_0430/result")
other_algo_dfs = {
    "S": pd.read_excel(os.path.join(csv_path, "gurobi_S.xlsx")),
    "M": pd.read_excel(os.path.join(csv_path, "gurobi_M.xlsx")),
    "L": pd.read_excel(os.path.join(csv_path, "gurobi_L.xlsx")),
}

result_base_paths = [result_base_path_1, result_base_path_2]
colors = ["b", "g", "m"]
labels = ["greedyV2", "greedyV3"]

instance_types = ["S", "M", "L"]
for instance_type in instance_types:
    other_algo_df = other_algo_dfs[instance_type]
    percentage_diffs = compare_obj(result_base_paths, other_algo_df, instance_type)

    # Check Threshold
    for i, diff in enumerate(percentage_diffs[1]):
        if diff <= 40:
            print(i, diff)

    plt.figure(figsize=(10, 6))
    for idx, percentage_diff in enumerate(percentage_diffs):
        average_percentage_diff = sum(percentage_diff) / len(percentage_diff)
        plt.plot(
            range(1, len(percentage_diff) + 1),
            percentage_diff,
            marker="o",
            linestyle="",
            color=colors[idx],
            label=f"{labels[idx]} (Avg: {average_percentage_diff:.2f}%)",
        )
        plt.axhline(
            y=average_percentage_diff,
            color=colors[idx],
            linestyle="--",
            label=f"{labels[idx]} Avg",
        )

    plt.xlabel("Instance Index")
    plt.ylabel("(Algorithm / Gurobi) % of Obj")
    plt.title(f"Percentage Difference of Best Obj for Instance Type {instance_type}")
    plt.grid(True)
    plt.axhline(y=100, color="k", linestyle="--")  # Add horizontal line at 100%
    plt.legend()
    plt.savefig(os.path.join(output_dir, f"percentage_difference_{instance_type}.png"))
    plt.close()  # Close the plot to avoid overlapping of figures
