# __Agents & NeoGPT 🕵️🤖__

## What is an Agent?

In artificial intelligence, an agent is a computer program or system that is designed to perceive its environment, make decisions and take actions to achieve a specific goal or set of goals. The agent operates autonomously, meaning it is not directly controlled by a human operator.

!!! info "Info"
    Agents are in very early stages of development. They may produce unexpected results or errors. Please use them with caution.

## Agents & NeoGPT

Agents are a new feature in NeoGPT. They are designed to be able to interact with the world around them. Currently there are only two agents, but more are planned to be added in the future.

## Agents in Focus

Agents within the NeoGPT ecosystem are designed to collaborate with the language model, enabling a broader range of interactions and problem-solving capabilities. Stay tuned for further updates and the introduction of additional agents, expanding the collaborative intelligence of NeoGPT.

## Meet the Agents

### __ML Engineer 🤖🧠__

The ML Engineer is a specialized agent for machine learning tasks, thinking like an experienced ML professional. It understands and solves various ML-related queries, making it a valuable asset for those needing support in Python programming, data science, and machine learning basics.

### __QA Engineer 🕵️🔍__

The QA Engineer, or Quality Assurance Engineer, is an agent with expertise in validating and assessing code and solutions. When presented with a problem, the QA Engineer can analyze the solution and provide feedback, helping to ensure the quality and correctness of the code.


## How to use Agents

Run the below command to see the agents in action.

=== "Command"
    ```bash title="Terminal"
    python main.py --task "Your task goes here"
    ```

=== "Example"
    ```bash title="Terminal"
    python main.py --task "Write a program to find the sum of all numbers stored in a list"
    ```


## How do Agents work?

1. The `hire()` method is like an assistant manager overseeing the collaboration between a machine learning (ML) specialist (ML Engineer) and a quality assurance (QA) expert (QA Engineer) to solve a task.

2. __Load Model__: The `hire()` function initiates by loading the machine learning model designed for the task.

3. __Collaboration Setup__: It establishes collaboration between two key roles - the ML Engineer and the QA Engineer.

4. __Task Assignment__: A task is assigned to the ML Engineer, who employs the loaded model to generate a solution.

5. __Quality Check__: The QA Engineer assesses the proposed solution for correctness and quality.

6. __Termination or Retry__: If the solution is approved, the program terminates. In case of disapproval, the process retries for a defined number of attempts.

7. __Collaborative Iteration__: Steps 3 to 5 are iteratively performed, facilitating collaboration until a satisfactory solution is achieved or attempts are exhausted.


