import sys
sys.path.append('../')
import utility as util
import copy
import math

E_MAX_INPUT = 100
G_MAX_INPUT = 133

def G_function(x):
  if x > G_MAX_INPUT:
    return 1
  else:
    return -0.000015 * (x**2) + 0.0095 * x
  
def E_function(x):
	if x > E_MAX_INPUT:
		return 40
	else:
	  return -0.004 * (x**2) + 0.8 * x


def greedy_best_location(iter_config: dict, candidates: list, compensate_attractiveness: list, cars_usage_record: list, total_util_list: list, verbose: bool = True):
    """
    Finds the best location to allocate resources based on maximizing utility until a point can no longer accommodate more resources.

    Args:
        iter_config (dict): A temporary copy of the configuration.
        candidates (list): List indicating whether a facility has been built.
        compensate_attractiveness (list): List representing compensation for attractiveness.
        cars_usage_record (list): Record of cars' usage.
        total_util_list (list): List representing total utility.
        verbose (bool, optional): Whether to print messages or not. Defaults to True.

    Returns:
        tuple: A tuple containing the updated configuration, the best objective value, the best location index, 
        the compensation for attractiveness at the best location, the record of cars' usage, and the updated total utility list.
    """
    best_iter_config, best_obj, best_loc = iter_config, -1, -1
    best_compensate_attractiveness, best_cars_usage_record, best_total_util_list = None, None, None

    # Find the best location with the highest objective value
    for ind, facility in enumerate(candidates):
        if facility == 0:  # If the facility hasn't been built yet, start filling with the largest utility (V)
            car_list = [(value, index) for index, value in enumerate(iter_config['V'][ind])]
            sorted_car_list = sorted(car_list, reverse=True)
            quota_loc = copy.deepcopy(iter_config['U_L'][ind])  
            quota_loc_k = copy.deepcopy(iter_config['U_LT'][ind])  
            quota_k = copy.deepcopy(iter_config['U_T'])  

            cur_to_fill = []
            cur_util = 0
            while quota_loc > 0:
                if len(sorted_car_list) == 0:
                    break  
                elif cur_util >= E_MAX_INPUT:
                    break  
                car_to_fill = sorted_car_list.pop(0)
                num_to_fill = min(quota_loc, quota_loc_k[car_to_fill[1]], quota_k[car_to_fill[1]], 
                                  math.ceil((E_MAX_INPUT-cur_util) / car_to_fill[0]))
                quota_k[car_to_fill[1]] -= num_to_fill
                quota_loc_k[car_to_fill[1]] -= num_to_fill
                quota_loc -= num_to_fill
                cur_util += num_to_fill * car_to_fill[0]
                cur_to_fill.append((car_to_fill[1], num_to_fill))

            # Update the temporary configuration and other related parameters
            cur_config = copy.deepcopy(iter_config)
            cur_config = update_config_each_iteration_build_j(cur_config, cur_to_fill)
            tmp_candidates = copy.deepcopy(candidates)
            tmp_candidates[ind] = 1
            tmp_compensate_attractiveness = copy.deepcopy(compensate_attractiveness)
            tmp_compensate_attractiveness[ind] = min(max(0, E_MAX_INPUT - cur_util), config['A_EX_bound'])
            if verbose:
                print(f"這次的cur_util:{cur_util}, 蓋多少廁所？{tmp_compensate_attractiveness[ind]}")
                print("compensate:", tmp_compensate_attractiveness)
            tmp_cars_usage_record = copy.deepcopy(cars_usage_record)
            tmp_cars_usage_record.extend([(x[0], x[1], ind) for x in cur_to_fill])
            tmp_total_util_list = copy.deepcopy(total_util_list)
            tmp_total_util_list[ind] = cur_util + tmp_compensate_attractiveness[ind]

            # Calculate the current objective value
            cur_obj = calc_current_gain(cur_config, tmp_candidates, tmp_total_util_list) - \
                      calc_current_cost(cur_config, tmp_candidates, tmp_compensate_attractiveness, tmp_cars_usage_record)
            if cur_obj > best_obj:
                best_obj = cur_obj
                best_loc = ind
                best_compensate_attractiveness = copy.deepcopy(tmp_compensate_attractiveness)
                best_cars_usage_record = copy.deepcopy(tmp_cars_usage_record)
                best_iter_config = cur_config
                best_total_util_list = copy.deepcopy(tmp_total_util_list)

    if verbose:
        print(f"Iteration ended! Found the best location: {best_loc}")
        print(f"Best obj: {best_obj}")
        
    return best_iter_config, best_obj, best_loc, best_compensate_attractiveness, best_cars_usage_record, best_total_util_list



def update_config_each_iteration_build_j(config: dict, cars_to_fill: list):
    """
    Update the configuration after allocating cars to fill a facility.

    Args:
        config (dict): The current configuration.
        cars_to_fill (list): List of tuples indicating the car types and the number to allocate.

    Returns:
        dict: Updated configuration after allocating cars.
    """
    for (car_type, allocate_num) in cars_to_fill:
        config['U_T'][car_type] -= allocate_num
    return config


def calc_current_gain(config: dict, facility_is_built: list, total_util_list: list):
    """
    Calculate the current gain based on the configuration, built facilities, and total utility list.

    Args:
        config (dict): The current configuration.
        facility_is_built (list): List indicating whether a facility is built.
        total_util_list (list): List representing total utility.

    Returns:
        float: Total gain.
    """
    total_gain = 0
    for customer_pt_i in range(config["i_amount"]):
        total_attr_i, our_vs_all_percentage = calc_total_attr_i(config, customer_pt_i, facility_is_built, total_util_list)
        customer_gain = config['H'][customer_pt_i] * G_function(total_attr_i) * our_vs_all_percentage
        total_gain += customer_gain
        print(f"Customer point {customer_pt_i}: total_attr={total_attr_i}, G={G_function(total_attr_i)}, Our percentage={our_vs_all_percentage}, Earned money={customer_gain}")
    print(f"Total earned money: {total_gain}")
    return total_gain


def calc_total_attr_i(config: dict, customer_pt_i: int, facility_is_built: list, total_util_list: list):
    """
    Calculate the total attractiveness for a given customer point i and our facility vs all facilities ratio.

    Args:
        config (dict): The current configuration.
        customer_pt_i (int): Index of the customer point.
        facility_is_built (list): List indicating whether a facility is built.
        total_util_list (list): List representing total utility.

    Returns:
        tuple: A tuple containing the total attractiveness for the customer point i and our facility vs all facilities ratio.
    """
    total_attr_i = 0

    # Calculate attractiveness contributed by our facilities
    for j_idx, facility in enumerate(facility_is_built):
        if facility == 1:
            total_attr_i += E_function(total_util_list[j_idx]) / (config['D'][customer_pt_i][j_idx] ** 2)

    only_our_facilities_total_attr = total_attr_i  # Temporary total attractiveness contributed only by our facilities

    # Add attractiveness contributed by opponents' facilities
    for l_idx in range(config['l_amount']):
        total_attr_i += config['A_opponent_bar'][l_idx] / (config['D_comp'][customer_pt_i][l_idx] ** 2)

    our_vs_all_percentage = only_our_facilities_total_attr / total_attr_i  # Calculate the ratio of our facilities' attractiveness to all facilities'

    return total_attr_i, our_vs_all_percentage


def calc_current_cost(config: dict, facility_is_built: list, compensate_attractiveness: list, cars_usage_record: list):
    """
    Calculate the current cost based on the configuration, built facilities, compensation for attractiveness, and cars usage record.

    Args:
        config (dict): The current configuration.
        facility_is_built (list): List indicating whether a facility is built.
        compensate_attractiveness (list): List representing compensation for attractiveness.
        cars_usage_record (list): Record of cars' usage.

    Returns:
        float: Total current cost.
    """
    total_cost = 0

    # Calculate cost for building facilities
    build_cost = sum(x * y for x, y in zip(facility_is_built, config['F']))

    # Calculate cost for compensating attractiveness
    attr_cost = sum(x * y for x, y in zip(compensate_attractiveness, config['C']))

    # Calculate cost for using cars
    for (car_type, allocate_num, loc_j) in cars_usage_record:
        total_cost += config['B'][loc_j][car_type] * allocate_num

    total_cost += build_cost + attr_cost
    
    # Print cost breakdown
    print(f"Build cost: {build_cost}, Attractiveness compensation cost: {attr_cost}, Cars usage cost: {total_cost - build_cost - attr_cost}, Total cost: {total_cost}\n")

    return total_cost



if __name__ == "__main__":
   	config = util.load_specific_yaml('./bingray_instance0429/instance_S_1.yaml')
	improve = True
	overall_best_obj = 0
	candidates = [0 for i in range(config['j_amount'])]
	compensate_attractiveness = [0 for i in range(config['j_amount'])]   # addition attr to fulfill e 
	total_util_list = [0 for i in range(config['j_amount'])]  # 紀錄每個點的總attr (車子+廁所)
	cars_usage_record = []  # 紀錄每次分了多少車給哪個j [(1, 5, 18),(0, 4, 18),(2, 3, 18),(2, 5, 2),...] (第k種車, 幾輛, 給哪個j)
	while (improve and any(element != 1 for element in candidates)):  #每輪多建一個點
		print("下一輪開始")
		print(compensate_attractiveness)
		improve = False
		iter_best_config = copy.deepcopy(config)
		cur_config, cur_obj, cur_loc_to_build, cur_compensate_attractiveness, cur_cars_usage_record, cur_total_util_list = greedy_best_location(iter_best_config, candidates, compensate_attractiveness, cars_usage_record, total_util_list)
		print(cur_compensate_attractiveness)
		print(f"current obj: {cur_obj}, loc_to_build: {cur_loc_to_build}")
		if cur_obj > overall_best_obj:
			improve = True
			config.update(cur_config)  #不確定update能不能，不能就改deepcopy!!!!!!!!!!!!!!
			overall_best_obj = cur_obj
			candidates[cur_loc_to_build] = 1
			compensate_attractiveness = copy.deepcopy(cur_compensate_attractiveness)
			cars_usage_record = copy.deepcopy(cur_cars_usage_record)
			total_util_list = copy.deepcopy(cur_total_util_list)
		print("\n\n這輪的結果：")
		print("建築蓋了沒的list：", candidates)
		print("車子使用紀錄：", cars_usage_record)
		print("蓋廁所總表：", compensate_attractiveness)
		print("效用總表對於每個點：", total_util_list)
		
	print(f"最終結果overall_best_obj:{overall_best_obj}")

