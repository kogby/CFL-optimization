import matplotlib.pyplot as plt
import yaml
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, "plots_instance_loc")

for ins in range(1, 101):
    yaml_file = os.path.join(
        current_dir,
        "Benchmark-Test",
        "OG_Model_0430",
        "instance",
        "S",
        f"instance_S_{ins}.yaml",
    )
    with open(yaml_file, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
        # Extracting positions
        customers = data.get("CONSUMERS", [])
        competitors = data.get("COMPETITORS", [])
        candidates = data.get("CANDIDATES", [])

    yaml_file = os.path.join(
        current_dir,
        "Benchmark-Test",
        "OG_Model_0430",
        "result",
        "greedyV2",
        "S",
        f"result_S_{ins}.yaml",
    )
    with open(yaml_file, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
        built_result = data.get("best_Y", None)

    # Plotting the positions
    plt.figure(figsize=(10, 10))

    # Plot customers
    customer_x, customer_y = zip(*customers)
    plt.scatter(customer_x, customer_y, c="blue", label="Customers", marker="o")

    # Plot competitors
    competitor_x, competitor_y = zip(*competitors)
    plt.scatter(competitor_x, competitor_y, c="red", label="Competitors", marker="x")

    # Plot candidates
    candidate_x, candidate_y = zip(*candidates)
    plt.scatter(candidate_x, candidate_y, c="green", label="Locations", marker="s")

    for ind, act in enumerate(built_result):
        if act == 1:
            best_x, best_y = candidates[ind]
            plt.scatter(best_x, best_y, c="yellow", marker="*", s=200)

    # Adding labels and legend
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, f"loc_{ins}.png"))
    plt.close()
