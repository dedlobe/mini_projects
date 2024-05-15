# Summary
The code is designed to read a file containing expressions written in a custom language called "R++" (Reverse Polish Notation with Python-like operators), and then convert these expressions into Python equivalents. The expressions in the file are used to calculate the values of two variables, x and y.

# Explanation

 ### 1. rpp_to_python function:

- This function takes two arguments: an R++ expression (expression) and the current value of ```x (x_value)```. It performs the following actions:

- Defines a regular expression `(regex)` that matches any arithmetic operator ```(+, -, *, /)```.

- Creates a replacement function `(replacement)` that replaces the matched operator with its opposite.
 
     - > **For example, + becomes -, - becomes +, etc.**

- Uses the `re.sub` function to substitute all occurrences of operators in the expression with their corresponding opposites according to the replacement function.

- Replaces all occurrences of the `variable x` in the expression with its current value `(x_value)` using `re.sub`.

- Tries to evaluate the resulting Python expression using `eval`.
  - If the evaluation is successful, it returns the result.
  - If there's an error during evaluation (e.g., syntax error, division by zero, or undefined variable), it returns an error message indicating the specific exception encountered.

### 2. calculate_final_amount_from_file function:

- This function takes the path to a file containing R++ expressions `(file_path)` as input.
  -  **Here's what it does:**

       - Opens the file in read mode ('r') and reads all lines into a list `(expressions)`.

       - Checks if the number of lines in the file is between 4 and 10 (inclusive). If not, it prints an error message and returns empty dictionaries for `final_values` and` problematic_expressions`.

  - Initializes two empty dictionaries:

       - `final_values`: This dictionary will store the final calculated values of variables (x and potentially y).
       - `problematic_expressions`: This list will store any expressions that encounter errors during processing.
Initializes a variable `x_value` to None, which will hold the current value of x.

  - Iterates through each line of expressions in the file:

       - Removes any leading or trailing whitespaces from the line using `strip`.
       - Checks for empty lines and adds them to `problematic_expressions` if found.
       - Uses regular expressions to check for consecutive operators (more than one in a row) and unbalanced parentheses in the expression.
       -  If found, adds the line number and error message to `problematic_expressions`.
       - Splits the line at the first occurrence of = to separate variable assignment (if present).
  
            - If the left-hand side is x, it calls the `rpp_to_python` function to calculate the value of x and updates` x_value` if the calculation is successful. Any errors are added to` problematic_expressions`.
              
            - If the left-hand side is y, it checks if `x_value` has already been calculated. If not, it adds "Value of x not found" error to `problematic_expressions`. Otherwise, it calculates the value of y using `rpp_to_python`and updates `final_values` if successful. Errors are added to `problematic_expressions`.
             
            - If the left-hand side is not x or y, it adds an "Invalid variable name" error to `problematic_expressions`.

            - If there's no = in the line (i.e., no assignment), it adds an "Invalid expression format" error to `problematic_expressions`.  
- Returns the calculated final values `(final_values)` and a list of encountered problems `(problematic_expressions`.

### 3. Main program:

- It defines the path to the input file `(input_file_path)`. It then calls the `calculate_final_amount_from_file` function to process the file.

    - If final_values is not empty `(meaning calculations were successful)`, it iterates through each key-value pair and prints the final value of each variable (x and potentially y).
    - If there are problematic expressions `(problematic)`, it prints a header "Invalid Expressions:" and then lists the line number and error message for each problematic expression.
