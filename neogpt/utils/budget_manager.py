from neogpt.config import PROJECT_COST, TOTAL_COST

# Define a function to manage the budget of the project 
def budget_manager():
    return "Budget Manager"



def final_cost():
    global PROJECT_COST
    PROJECT_COST += TOTAL_COST + 200 # AI Labour Cost 😂 JFF why not
    return PROJECT_COST
