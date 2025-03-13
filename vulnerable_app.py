import pickle
import subprocess
import os

# Hardcoded secret (vulnerability)
SECRET_KEY = "my_super_secret_key"

def insecure_deserialization(data):
    # Insecure deserialization using pickle (vulnerability)
    return pickle.loads(data)

def run_command(command):
    # Shell injection vulnerability (vulnerability)
    return subprocess.run(command, shell=True)

def evaluate_expression(expression):
    # Use of eval (vulnerability)
    return eval(expression)

def check_condition(value):
    # Use of assert (vulnerability)
    assert value > 0, "Value must be positive"
    return value

# Example usage
if __name__ == "__main__":
    # Simulate insecure deserialization
    serialized_data = b"cos\nsystem\n(S'echo Vulnerable!'\ntR."
    insecure_deserialization(serialized_data)

    # Simulate shell injection
    user_input = input("Enter a command: ")
    run_command(user_input)

    # Simulate eval usage
    user_expression = input("Enter an expression: ")
    result = evaluate_expression(user_expression)
    print("Result:", result)

    # Simulate assert usage
    check_condition(-1)