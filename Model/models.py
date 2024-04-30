from gurobipy import Model, GRB, quicksum
import math

"""
Decision Variables
===============================
y : Whether location j build facility or not, Dim: (j) , BINARY
x : The amount of resource k allocated to location j, Dim: (j,k), CONTINUOUS
aX : Extra attractiveness allocated to location j, Dim: (j), CONTINUOUS
===============================

Other Variables
u : Utility of facility j to customer point i, Dim:(i, j), CONTINUOUS
P : Probability of customer i choosing facility j, Dim : (i, j), CONTINUOUS
TA : Total Attractiveness for customer location i, Dim : (i), CONTINUOUS
===============================

Model Names:
OG: Original Problem
LR: Lagragne Relaxed Problem

RF_1 : Reformulated: TAI => 1 - fraction
E : Whether or not contain E function
G : Whether or not contain G function 
"""


def OG_RF_1_G(config: dict):
    """
    Model  (G, reformulate)
    """
    I = set(range(0, config["i_amount"]))
    J = set(range(0, config["j_amount"]))
    K = set(range(0, config["k_amount"]))
    L = set(range(0, config["l_amount"]))

    model = Model("Competitive Facility Location")
    model.setParam("NumericFocus", 3)
    y = model.addVars(J, vtype=GRB.BINARY, name="y")  # 3.14
    x = model.addVars(J, K, vtype=GRB.CONTINUOUS, name="x", lb=0)  # 3.12
    aX = model.addVars(J, vtype=GRB.CONTINUOUS, name="aX", lb=0)  # 3.13

    u = model.addVars(
        I, J, vtype=GRB.CONTINUOUS, name="utility(u)", lb=0
    )  # utility var(3.5)
    P = model.addVars(
        I, J, vtype=GRB.CONTINUOUS, name="P, opponent vs TA ratio", lb=0.0, ub=1.0
    )  # 改這裡
    TA = model.addVars(I, vtype=GRB.CONTINUOUS, name="TA", lb=0.00000000)
    TAi_lambda = model.addVars(
        I,
        vtype=GRB.CONTINUOUS,
        name="negative TAi*lambda(e's power)",
        lb=-100000,
        ub=-0.000001,
    )  # -lambda*TAi
    G_exp_vars = model.addVars(
        I, vtype=GRB.CONTINUOUS, name="G_exp_vars", lb=0.0, ub=1
    )  # e^-(lambda*TAi), ub=0.5

    model.update()

    model.addConstrs(
        (x[j, k] <= config["U_LT"][j][k] * y[j] for j in J for k in K),
        "(3.1) Resource only for built facility, and amount of type k for facility j is limit at U_LT[j, k]",
    )
    model.addConstrs(
        (quicksum(x[j, k] for j in J) <= config["U_T"][k] for k in K),
        "(3.2) The total amount of resource k is U_T[k]",
    )
    model.addConstrs(
        (quicksum(x[j, k] for k in K) <= config["U_L"][j] for j in J),
        "(3.3) The max resource sum for facility j is U_L[j]",
    )
    model.addConstrs(
        (aX[j] <= config["A_EX_bound"] * y[j] for j in J),
        "(3.4) Extra Attractiveness Limit",
    )

    model.addConstrs(
        (
            u[i, j]
            == (
                (quicksum(config["V"][j][k] * x[j, k] for k in K) + aX[j])
                / (config["D"][i][j] ** 2)
            )
            for i in I
            for j in J
        ),
        "(3.5) utility for facility j to customer i",
    )
    ## TA的限制式, 因為不能讓 G_exp中 addGenConstrExp內的變數為多個變數的線性組合所以要另外創TA變數
    model.addConstrs(
        (
            TA[i]
            == quicksum(u[i, j] for j in J)
            + (
                quicksum(
                    config["A_opponent_bar"][l] / (config["D_comp"][i][l] ** 2)
                    for l in L
                )
            )
            for i in I
        ),
        "(3.7) calculate total TA by u and A_bar",
    )

    model.addConstrs(
        (
            (
                quicksum(
                    config["A_opponent_bar"][l] / (config["D_comp"][i][l] ** 2)
                    for l in L
                )
            )
            == P[i, j] * TA[i]
            for i in I
            for j in J
        ),
        "A_opponent對比TAI, 分母要是常數所以用乘的",
    )

    ## G的計算
    # def G(tai):
    #     return 1 - np.exp(-config['lambda_for_G'] * tai)
    model.addConstrs(
        (TAi_lambda[i] == (-config["lambda_for_G"] * TA[i]) for i in I),
        "negative tai*lambda constr",
    )
    # Gurobi無法直接在目標式有exponential
    for i in I:
        model.addGenConstrExpA(
            TAi_lambda[i], G_exp_vars[i], math.e, name=f"G_exp_constr_{i}"
        )
    # Objective function: Maximize profit by attracting customers - costs
    objective = (
        quicksum(
            config["H"][i] * (1 - G_exp_vars[i]) * (1 - quicksum(P[i, j] for j in J))
            for i in I
        )
    ) - (
        quicksum(
            config["F"][j] * y[j]
            + config["C"][j] * aX[j]
            + quicksum(config["B"][j][k] * x[j, k] for k in K)
            for j in J
        )
    )
    model.setObjective(objective, GRB.MAXIMIZE)

    return model


def OG_RF_1_GE(config: dict):
    """
    Model  (add G, reformulate, add E)
    """
    I = set(range(0, config["i_amount"]))
    J = set(range(0, config["j_amount"]))
    K = set(range(0, config["k_amount"]))
    L = set(range(0, config["l_amount"]))

    model = Model("Competitive Facility Location")
    model.setParam("NumericFocus", 3)
    y = model.addVars(J, vtype=GRB.BINARY, name="y")  # 3.14
    x = model.addVars(J, K, vtype=GRB.CONTINUOUS, name="x", lb=0)  # 3.12
    aX = model.addVars(J, vtype=GRB.CONTINUOUS, name="aX", lb=0)  # 3.13

    u = model.addVars(
        I, J, vtype=GRB.CONTINUOUS, name="utility(u)", lb=0
    )  # utility var(3.5)
    P = model.addVars(
        I, J, vtype=GRB.CONTINUOUS, name="P, opponent vs TA ratio", lb=0.0, ub=1.0
    )  # 改這裡
    TA = model.addVars(I, vtype=GRB.CONTINUOUS, name="TA", lb=0.00000000)
    TAi_lambda = model.addVars(
        I,
        vtype=GRB.CONTINUOUS,
        name="negative TAi*lambda(e's power)",
        lb=-100000,
        ub=-0.000001,
    )  # -lambda*TAi
    G_exp_vars = model.addVars(
        I, vtype=GRB.CONTINUOUS, name="G_exp_vars", lb=0.0, ub=1
    )  # e^-(lambda*TAi), ub=0.5

    place_utility = model.addVars(J, vtype=GRB.CONTINUOUS, name="place_utility", lb=0)

    model.update()

    model.addConstrs(
        (x[j, k] <= config["U_LT"][j][k] * y[j] for j in J for k in K),
        "(3.1) Resource only for built facility, and amount of type k for facility j is limit at U_LT[j, k]",
    )
    model.addConstrs(
        (quicksum(x[j, k] for j in J) <= config["U_T"][k] for k in K),
        "(3.2) The total amount of resource k is U_T[k]",
    )
    model.addConstrs(
        (quicksum(x[j, k] for k in K) <= config["U_L"][j] for j in J),
        "(3.3) The max resource sum for facility j is U_L[j]",
    )
    model.addConstrs(
        (aX[j] <= config["A_EX_bound"] * y[j] for j in J),
        "(3.4) Extra Attractiveness Limit",
    )

    model.addConstrs(
        (
            place_utility[j] == quicksum(config["V"][j][k] * x[j, k] for k in K) + aX[j]
            for j in J
        ),
        "place utility before e",
    )

    model.addConstrs(
        (
            u[i, j]
            == (
                (-0.0000007 * place_utility[j] ** 2 + 1.1 * place_utility[j])
                / (config["D"][i][j] ** 2)
            )
            for i in I
            for j in J
        ),
        "(3.5) utility for facility j to customer i加入e以後",
    )

    ## TA的限制式, 因為不能讓 G_exp中 addGenConstrExp內的變數為多個變數的線性組合所以要另外創TA變數
    model.addConstrs(
        (
            TA[i]
            == quicksum(u[i, j] for j in J)
            + (
                quicksum(
                    config["A_opponent_bar"][l] / (config["D_comp"][i][l] ** 2)
                    for l in L
                )
            )
            for i in I
        ),
        "(3.7) calculate total TA by u and A_bar",
    )

    model.addConstrs(
        (
            (
                quicksum(
                    config["A_opponent_bar"][l] / (config["D_comp"][i][l] ** 2)
                    for l in L
                )
            )
            == P[i, j] * TA[i]
            for i in I
            for j in J
        ),
        "A_opponent對比TAI, 分母要是常數所以用乘的",
    )

    ## G的計算
    # def G(tai):
    #     return 1 - np.exp(-config['lambda_for_G'] * tai)
    model.addConstrs(
        (TAi_lambda[i] == (-config["lambda_for_G"] * TA[i]) for i in I),
        "negative tai*lambda constr",
    )
    # Gurobi無法直接在目標式有exponential
    for i in I:
        model.addGenConstrExpA(
            TAi_lambda[i], G_exp_vars[i], math.e, name=f"G_exp_constr_{i}"
        )

    # Objective function: Maximize profit by attracting customers - costs
    objective = (
        quicksum(
            config["H"][i] * (1 - G_exp_vars[i]) * (1 - quicksum(P[i, j] for j in J))
            for i in I
        )
    ) - (
        quicksum(
            config["F"][j] * y[j]
            + config["C"][j] * aX[j]
            + quicksum(config["B"][j][k] * x[j, k] for k in K)
            for j in J
        )
    )
    model.setObjective(objective, GRB.MAXIMIZE)

    return model


def OG_G(config: dict):
    """
    Model (G, no reformulate)
    """
    I = set(range(0, config["i_amount"]))
    J = set(range(0, config["j_amount"]))
    K = set(range(0, config["k_amount"]))
    L = set(range(0, config["l_amount"]))

    model = Model("Competitive Facility Location")
    model.setParam("NumericFocus", 3)
    y = model.addVars(J, vtype=GRB.BINARY, name="y")  # 3.14
    x = model.addVars(J, K, vtype=GRB.CONTINUOUS, name="x", lb=0)  # 3.12
    aX = model.addVars(J, vtype=GRB.CONTINUOUS, name="aX", lb=0)  # 3.13

    u = model.addVars(
        I, J, vtype=GRB.CONTINUOUS, name="utility(u)", lb=0
    )  # utility var(3.5)
    P = model.addVars(
        I, J, vtype=GRB.CONTINUOUS, name="P, utility vs TA ratio", lb=0.0, ub=1.0
    )  # Probability of i choosing j
    TA = model.addVars(I, vtype=GRB.CONTINUOUS, name="TA", lb=0.00000000)
    TAi_lambda = model.addVars(
        I,
        vtype=GRB.CONTINUOUS,
        name="negative TAi*lambda(e's power)",
        lb=-100000,
        ub=-0.000001,
    )  # -lambda*TAi
    G_exp_vars = model.addVars(
        I, vtype=GRB.CONTINUOUS, name="G_exp_vars", lb=0.0, ub=1
    )  # e^-(lambda*TAi), ub=0.5

    model.update()

    model.addConstrs(
        (x[j, k] <= config["U_LT"][j][k] * y[j] for j in J for k in K),
        "(3.1) Resource only for built facility, and amount of type k for facility j is limit at U_LT[j, k]",
    )
    model.addConstrs(
        (quicksum(x[j, k] for j in J) <= config["U_T"][k] for k in K),
        "(3.2) The total amount of resource k is U_T[k]",
    )
    model.addConstrs(
        (quicksum(x[j, k] for k in K) <= config["U_L"][j] for j in J),
        "(3.3) The max resource sum for facility j is U_L[j]",
    )
    model.addConstrs(
        (aX[j] <= config["A_EX_bound"] * y[j] for j in J),
        "(3.4) Extra Attractiveness Limit",
    )

    model.addConstrs(
        (
            u[i, j]
            == (
                (quicksum(config["V"][j][k] * x[j, k] for k in K) + aX[j])
                / (config["D"][i][j] ** 2)
            )
            for i in I
            for j in J
        ),
        "(3.5) utility for facility j to customer i",
    )
    model.addConstrs(
        (u[i, j] == P[i, j] * TA[i] for i in I for j in J),
        "(3.8) calculate P by uij/TAi, 分母要是常數所以用乘的",
    )
    ## TA的限制式, 因為不能讓 G_exp中 addGenConstrExp內的變數為多個變數的線性組合所以要另外創TA變數
    model.addConstrs(
        (
            TA[i]
            == quicksum(u[i, j] for j in J)
            + (
                quicksum(
                    config["A_opponent_bar"][l] / (config["D_comp"][i][l] ** 2)
                    for l in L
                )
            )
            for i in I
        ),
        "(3.7) calculate total TA by u and A_bar",
    )

    ## G的計算
    # def G(tai):
    #     return 1 - np.exp(-config['lambda_for_G'] * tai)
    model.addConstrs(
        (TAi_lambda[i] == (-config["lambda_for_G"] * TA[i]) for i in I),
        "negative tai*lambda constr",
    )
    # Gurobi無法直接在目標式有exponential
    for i in I:
        model.addGenConstrExpA(
            TAi_lambda[i], G_exp_vars[i], math.e, name=f"G_exp_constr_{i}"
        )

    # Objective function: Maximize profit by attracting customers - costs
    objective = (
        quicksum(
            config["H"][i] * (1 - G_exp_vars[i]) * (quicksum(P[i, j] for j in J))
            for i in I
        )
    ) - (
        quicksum(
            config["F"][j] * y[j]
            + config["C"][j] * aX[j]
            + quicksum(config["B"][j][k] * x[j, k] for k in K)
            for j in J
        )
    )
    model.setObjective(objective, GRB.MAXIMIZE)
    return model


def OG_GE_RF2(config: dict):
    """
    Model (G, reformulate, add E)
    4/24 New G and E
    """
    I = config["i_amount"]
    J = config["j_amount"]
    K = config["k_amount"]
    L = config["l_amount"]
    config['A_comp'] = config['A_opponent_bar']
    config['M'] = config["A_EX_bound"]
    m = Model("Competitive Facility Location")
    X = []
    for j in range(J):
        temp = []
        for k in range(K):
            temp.append(
                m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="X_" + str(j) + "_" + str(k))
            )
        X.append(temp)

    A_EX = []
    for j in range(J):
        A_EX.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="A^X_" + str(j)))

    Y = []
    for j in range(J):
        Y.append(m.addVar(vtype=GRB.BINARY, lb=0, name="Y_" + str(j)))

    E_var = []
    for j in range(J):
        E_var.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="E_var_" + str(j)))

    G_var = []
    for i in range(I):
        G_var.append(m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=1, name="G_var_" + str(i)))

    TA = {}
    for i in range(I):
        TA[i] = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="TA_" + str(i))

    W = {}
    for i in range(I):
        W[i] = m.addVar(vtype=GRB.CONTINUOUS, lb=0, name="W_" + str(i))

    ## Integrate new variables
    m.update()

    ## Set objective
    m.setObjective(
        quicksum(W[i] for i in range(I))
        - quicksum(
            config["F"][j] * Y[j]
            + config["C"][j] * A_EX[j]
            + quicksum(config["B"][j][k] * X[j][k] for k in range(K))
            for j in range(J)
        ),
        GRB.MAXIMIZE,
    )

    ## Add constraints:
    for j in range(J):
        m.addConstr(
            E_var[j]
            == quicksum(config["V"][j][k] * X[j][k] for k in range(K)) + A_EX[j],
            "define_E_var_" + str(j),
        )

    for i in range(I):
        m.addConstr(
            G_var[i] <= -0.000015 * TA[i] ** 2 + 0.0095 * TA[i],
            "define_G_var_" + str(i),
        )

    for i in range(I):
        m.addConstr(
            TA[i]
            == quicksum(
                (-0.004 * E_var[j] ** 2 + 0.8 * E_var[j]) / config['D'][i][j] ** 2
                for j in range(J)
            )
            + quicksum(
                config["A_comp"][l] / config["D_comp"][i][l] ** 2 for l in range(L)
            ),
            "define_TA_" + str(i),
        )
    # ???
    ALPHA = [1 for x in range(I)]
    for i in range(I):
        m.addConstr(
            W[i] * TA[i]
            == config["H"][i] * G_var[i] * TA[i]
            - config["H"][i]
            * ALPHA[i]
            * quicksum(
                config["A_comp"][l] / config["D_comp"][i][l] ** 2 for l in range(L)
            ),
            "define_W_" + str(i),
        )

    for j in range(J):
        for k in range(K):
            m.addConstr(
                X[j][k] <= config["U_LT"][j][k] * Y[j],
                "build_to_allocate_" + str(j) + "_" + str(k),
            )

    for k in range(K):
        m.addConstr(
            quicksum(X[j][k] for j in range(J)) <= config["U_T"][k],
            "car_amount_limit_" + str(k),
        )

    for j in range(J):
        m.addConstr(
            quicksum(X[j][k] for k in range(K)) <= config["U_L"][j],
            "facility_limit_" + str(j),
        )

    for j in range(J):
        m.addConstr(
            A_EX[j] <= config["A_EX_bound"] * Y[j], "decoration_limit_" + str(j)
        )
    return m