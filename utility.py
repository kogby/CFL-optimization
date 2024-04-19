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
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
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
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data