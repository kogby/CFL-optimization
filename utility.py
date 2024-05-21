import sys
import os
import yaml
import math
import random
import numpy as np
from path_config import INSTANCES_DIR


def cal_distance(point_1, point_2, cal_method="euclidean"):
    """
    Calculate the distance between two points.

    Args:
    - point_1 (tuple): The coordinates of the first point.
    - point_2 (tuple): The coordinates of the second point.
    - cal_method (str, optional): The method to use for distance calculation.
      Can be "euclidean" (default) or "manhattan".

    Returns:
    - distance (float): The calculated distance between the two points.
    """

    x1, y1 = point_1
    x2, y2 = point_2
    if cal_method == "euclidean":
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    elif cal_method == "manhattan":
        distance = abs(x2 - x1) + abs(y2 - y1)
    return round(distance, 2)


def create_points(num_points, map_size):
    """
    Generate random points on the map.

    Args:
    - num_points (int): The number of points to generate.

    Returns:
    - points (list of tuples): List of generated points.
    """
    points = []
    for _ in range(num_points):
        x = np.random.randint(map_size)
        y = np.random.randint(map_size)
        points.append((x, y))
    return points


def dist_list_generator(customers, locations):
    """
    Generate a 2D array of distances between customers and locations.

    Args:
    - customers (list of tuples): List of tuples representing customer coordinates.
    - locations (list of tuples): List of tuples representing location coordinates.

    Returns:
    - distances (2D numpy array): Array of distances between each customer and location.
    """
    # Initialize a 2D array to store distances
    distances = np.zeros((len(customers), len(locations)))

    # Calculate distances between each customer and each location
    for i, customer in enumerate(customers):
        for j, location in enumerate(locations):
            distances[i][j] = cal_distance(customer, location)
    return distances


def load_specific_yaml(filename):
    """
    Load the content of a YAML file from the instances folder.

    Parameters:
    filename (str): 在 instances 資料夾中的 YAML 檔案名。

    Returns:
    dict: YAML 檔案內容。
    """
    file_path = os.path.join(INSTANCES_DIR, filename)
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return data


def save_yaml(data, filename):
    """
    Save data to a YAML file in the instances folder.

    Args:
    - data (dict): The data to save to the file.
    - filename (str): The name of the file to save the data to.
    """
    file_path = os.path.join(INSTANCES_DIR, filename)
    with open(file_path, "w") as file:
        yaml.dump(data, file, default_flow_style=False)


def run_experiments(
    instance_path, result_path, algorithm, instance_types, instance_num, verbose=1
):
    print(
        f"Running experiments -> | algorithm:  {algorithm.__name__} | instance_types: {' '.join(instance_types)}"
    )

    for instance_type in instance_types:
        for i in range(1, instance_num + 1):
            print(f"Instance {instance_type}_{i}/100")
            config_path = os.path.join(
                instance_path, instance_type, f"instance_{instance_type}_{i}.yaml"
            )
            result = algorithm(config_path, verbose)
            result_dir = os.path.join(result_path, instance_type)
            os.makedirs(result_dir, exist_ok=True)
            result_file = os.path.join(result_dir, f"result_{instance_type}_{i}.yaml")
            save_yaml(result, result_file)
            print(f"Saved result for instance {instance_type}_{i} to {result_path}")
            print("!!! instance end !!!")
            print("=====================================================================\n\n")
