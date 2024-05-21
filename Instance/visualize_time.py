"""This file is used to plot the execution time of each instance(S,M,L)"""
import os
import yaml
import matplotlib.pyplot as plt
import pandas as pd


def plot_spend_time(
    result_base_path, instance_types, output_dir=None, instance_num=100
):
    for instance_type in instance_types:
        spend_times = []
        output_file = os.path.join(output_dir, f"spend_time_{instance_type}.png")

        for i in range(1, instance_num + 1):
            result_path = os.path.join(
                result_base_path, instance_type, f"result_{instance_type}_{i}.yaml"
            )
            if os.path.exists(result_path):
                with open(result_path, "r") as file:
                    result_data = yaml.full_load(file)
                    spend_time = result_data.get("spend_time(s)", None)
                if spend_time is not None:
                    spend_times.append(spend_time)

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.scatter([i for i in range(1, len(spend_times) + 1)], spend_times)
        plt.xlabel("Instance Index")
        plt.ylabel("Spend Time (s)")
        plt.title(f"Spend Time for Instance Type {instance_type}")

        if output_file:
            plt.savefig(output_file)
        else:
            plt.show()


# Example usage
result_base_path = "Benchmark-Test/OG_Model_0430/result"
output_dir = "plots_greedyV1_vs_gurobi"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

instance_types = ["S", "M", "L"]

instance_num = 100
plot_spend_time(result_base_path, instance_types, output_dir, instance_num)
