import re

# ps. The valid variables in this file are considered to be x and y

def rpp_to_python(expression, x_value):
    # Replace R++ operators with Python equivalents
    regex = r"[+\-*/]"
    replacement = lambda match: {'+': '-', '-': '+', '*': '/', '/': '*'}.get(match.group())

    expression = re.sub(regex, replacement, expression)

    # Replace 'x' with its current value
    expression = re.sub(r'\bx\b', str(x_value), expression)

    try:
        # Evaluate the Python expression
        result = eval(expression)
        return result
    except (SyntaxError, ZeroDivisionError, NameError) as e:
        return f"Invalid expression: {e}"
    except Exception as e:
        return f"Error: {e}"


def calculate_final_amount_from_file(file_path):
    with open(file_path, 'r') as input_file:
        expressions = input_file.readlines()
    #num of lines should be between 4 to 10
    num_lines = len(expressions)

    if not (4 <= num_lines <= 10):
        print("Error: Number of lines in the file should be between 4 and 10 (inclusive).")
        return {}, []

    final_values = {}
    # List to store problematic expressions and their line numbers
    problematic_expressions = []

    # Variable to store the current value of x
    x_value = None

    for line_number, line in enumerate(expressions, start=1):
        expression = line.strip()

        if len(expression) == 0:
            problematic_expressions.append((line_number, "Empty line"))
            continue

        # Check for consecutive operators and unbalanced parentheses
        if re.search(r'[+\-*/]{2,}', expression.replace('(', '').replace(')', '')):
            problematic_expressions.append((line_number, "Consecutive operators"))
            continue
        if expression.count('(') != expression.count(')'):
            problematic_expressions.append((line_number, "Unbalanced parentheses"))
            continue

        # Separate assignments for x and y
        if '=' in expression:
            var, expr = expression.split('=')
            var = var.strip()
            expr = expr.strip()

            if var == 'x':
                # Calculate x
                x_result = rpp_to_python(expr, x_value)
                if isinstance(x_result, (int, float)):
                    final_values[f"{var} in Line {line_number}"] = x_result
                    x_value = x_result
                else:
                    problematic_expressions.append((line_number, x_result))
            elif var == 'y':
                # Calculate y using the previously calculated value of x
                if x_value is None:
                    problematic_expressions.append((line_number, "Value of x not found"))
                    continue

                y_result = rpp_to_python(expr, x_value)
                if isinstance(y_result, (int, float)):
                    final_values[f"{var} in Line {line_number}"] = y_result
                else:
                    problematic_expressions.append((line_number, y_result))
            else:
                problematic_expressions.append((line_number, "Invalid variable name"))
        else:
            problematic_expressions.append((line_number, "Invalid expression format"))

    return final_values, problematic_expressions


# File path containing R++ expressions
input_file_path = 'input.txt'

# Calculate the final values of x and y from the file
final_values, problematic = calculate_final_amount_from_file(input_file_path)

# Print the final values if they are valid
for var, val in final_values.items():
    print(f"{var} = {val}")

# Print problematic expressions and their errors
if problematic:
    print("\nInvalid Expressions:")
    for line_number, error in problematic:
        print(f"Line {line_number}: {error}")
