import re
import io
import signal
import sys
import ast
import warnings
import traceback
from PIL import Image
import importlib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from enum import Enum
from typing import Any, Dict, Optional, List
from llama_index.core.output_parsers.base import ChainableOutputParser
# from src.tools.data_analysis.prompts import DEFAULT_ANALYZE_PLOT_INSTRUCTION_STR

from ..custom_logging import logger

class ErrorHistory:
    def __init__(self):
        self.errors = []
    
    def add_error(self, error_message, code):
        self.errors.append({'error': error_message, 'code': code})
    
    def check_error(self, error_message):
        for record in self.errors:
            if record['error'] == error_message:
                return record['code']
        return None

error_history = ErrorHistory()
class TimeoutException(Exception):
    pass


class Status(Enum):
    NO_PLOT = "No plot"
    SHOW_PLOT_SUCCESS = "Show plot successfully!"
    SHOW_PLOT_FAILED = "Show plot failed!"

def parse_code_markdown(text: str, only_last: bool) -> List[str]:
    # Regular expression pattern to match code within triple-backticks with an optional programming language
    pattern = r"```[a-zA-Z]*\n(.*?)```"

    # Find all matches of the pattern in the text
    matches = re.findall(pattern, text, re.DOTALL)

    # Return the last matched group if requested
    code = matches[-1] if matches and only_last else matches

    # If empty, we optimistically assume the output is the code
    if not code:
        # Strip the text to handle cases where the code may start or end with triple backticks or quotes
        candidate = text.strip()

        # Handle cases where the code is surrounded by regular quotes
        if candidate.startswith('"') and candidate.endswith('"'):
            candidate = candidate[1:-1]

        if candidate.startswith("'") and candidate.endswith("'"):
            candidate = candidate[1:-1]

        if candidate.startswith("`") and candidate.endswith("`"):
            candidate = candidate[1:-1]

        # Handle triple backticks at the start
        if candidate.startswith("```"):
            candidate = re.sub(r"^```[a-zA-Z]*\n?", "", candidate)

        # Handle triple backticks at the end
        if candidate.endswith("```"):
            candidate = candidate[:-3]

        code = candidate.strip()

    return code
def extract_python_code(markdown_text)-> List[str]:
    pattern = r"```python(.*?)```"
    matches = re.findall(pattern, markdown_text, re.DOTALL)
    return "\n".join([match.strip() for match in matches])
def extract_python_codev2(markdown_text: str) -> str:
    pattern = r"```python(.*?)```"
    matches = re.findall(pattern, markdown_text, re.DOTALL)
    extracted_code = "\n".join([match.strip() for match in matches])
    
    # Fix indentation issues
    fixed_code = []
    lines = extracted_code.split('\n')
    indent_level = 0
    for line in lines:
        stripped_line = line.lstrip()
        if stripped_line.startswith("for ") or stripped_line.startswith("if "):
            indent_level += 1
            fixed_code.append(" " * 4 * (indent_level - 1) + stripped_line)
        elif line.strip() == "":
            fixed_code.append(line)
        else:
            fixed_code.append(" " * 4 * (indent_level) + stripped_line)
    return "\n".join(fixed_code)

def extract_python_codev4(markdown_text: str) -> str:
    pattern = r"```python(.*?)```"
    matches = re.findall(pattern, markdown_text, re.DOTALL)
    if not matches:
        # If no Python code is found, return the original markdown text
        return markdown_text
    extracted_code = "\n".join([match.strip() for match in matches])
    
    # Fix indentation issues
    fixed_code = []
    lines = extracted_code.split('\n')
    indent_stack = [0]  # Stack to maintain indentation level
    
    block_keywords = (
        'for ', 'if ', 'while ', 'def ', 'class ', 'elif ', 'else:', 'try:', 
        'except ', 'finally:', 'with ', 'match ', 'case '
    )
    
    for line in lines:
        stripped_line = line.lstrip()
        
        if any(stripped_line.startswith(keyword) for keyword in block_keywords):
            # Add the correct indentation and increase the indent level
            fixed_code.append(' ' * indent_stack[-1] + stripped_line)
            indent_stack.append(indent_stack[-1] + 4)
        elif stripped_line == '':
            fixed_code.append(line)  # Empty lines are kept as is
        else:
            # Maintain the current indentation level for other lines
            fixed_code.append(' ' * indent_stack[-1] + stripped_line)
        
        # Reduce indentation when the line ends with ":" or for single-line blocks
        if stripped_line and stripped_line[-1] != ':' and indent_stack[-1] > 0:
            indent_stack.pop()
    
    # Join the fixed lines of code
    return "\n".join(fixed_code)


# def show_plot() -> str:
#     try:
#         # Ensure there's a plot to display
#         # if not plt.get_fignums():
#         #     return Status.NO_PLOT
        
#         # Create an in-memory bytes buffer for the plot image
#         buffer = io.BytesIO()
#         plt.savefig(buffer, format='png')
#         buffer.seek(0)

#         # Clear the plot
#         plt.close()
        
#         # Display the plot image
#         image = cl.Image(
#             name="plot", 
#             size="large", 
#             #display="inline", 
#             content=buffer.getvalue())
        

#         run_sync(cl.Message(
#             content="",
#             elements=[image]
#         ).send())
        
#         return Status.SHOW_PLOT_SUCCESS
#     except Exception as e:
#         return Status.SHOW_PLOT_FAILED
    
# def show_plotv2(vision_llm:any) :
#     try:
#         buffer = io.BytesIO()
#         plt.savefig(buffer, format='png')
#         buffer.seek(0)
#         new_buffer=buffer.getvalue()

#         plt.close()
        
#         image = cl.Image(
#             name="plot", 
#             size="large", 
#             display="inline", 
#             content=new_buffer)
        
#         run_sync(cl.Message(
#             content="",
#             elements=[image]
#         ).send())

#         buffer.seek(0)
#         image_sequence = [Image.open(buffer)]

#         description = vision_llm.complete(
#         prompt=DEFAULT_ANALYZE_PLOT_INSTRUCTION_STR,
#         images= image_sequence,
#         )

#         run_sync(cl.Message(
#             content=f"\n\n{description}\n",

#         ).send())

#         return description
#     except Exception as e:
#         return Status.SHOW_PLOT_FAILED

def save_plot():#
    
    
    # Create an in-memory bytes buffer for the plot image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    # Clear the plot
    plt.close()
    
    return buffer

def timeout_handler(signum, frame):
    raise TimeoutException("Timed out!")

class InstructionParser(ChainableOutputParser):
    """Instruction parser for data analysis, model training, and evaluation."""

    def __init__(self, input_data:List[Dict],error_history: List[Dict[str, str]] = None, output_kwargs: Optional[Dict[str, Any]] = None) -> None:
        self.input_data= input_data
        self.error_history = error_history if error_history is not None else []
        self.output_kwargs = output_kwargs or {}
        logger.info(f"input data:{self.input_data}")
        

    def import_model(self, model_name: str):
        """Dynamically import a model class."""
        module_name, class_name = model_name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    def import_metric(self, metric_name: str):
        """Dynamically import a metric function."""
        module_name, func_name = metric_name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, func_name)

    def parse(self, output: str) -> Any:
        """Parse, validate, and correct errors programmatically."""
        logger.info("parsing!!!!")
        return self.default_output_processor(output, **self.output_kwargs)
    def parsev2(self, output: str,vision_llm:any) -> Any:
        """Parse, validate, and correct errors programmatically."""
        return self.output_processor_comprehensive_data_analysis(output, vision_llm,**self.output_kwargs)
    
    def default_output_processor(self, output: str, timeout: int = 1000, **output_kwargs: Any) -> str:
        """Process outputs in a default manner with a timeout."""
        if sys.version_info < (3, 9):
            logger.warning(
                "Python version must be >= 3.9 in order to use "
                "the default output processor, which executes "
                "the Python query. Instead, we will return the "
                "raw Python instructions as a string."
            )
            return output

        local_vars = {
            "input_data": self.input_data,
            "pd": pd,

        }
        global_vars = {}

        #output = parse_code_markdown(output, only_last=False)
        output=extract_python_code(output)
        logger.info(f"This is code generated by agent: {output}")
        
        # Redirect standard output to capture print statements
        old_stdout = sys.stdout
        sys.stdout = new_stdout = io.StringIO()
        

        try:
            # Set a timeout for the execution
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)

                # Attempt to execute the code directly without AST parsing first
                logger.info(f"Executing generated code:\n{output}")
                exec(output, global_vars, local_vars)

            
            # Capture any printed output
            printed_output = new_stdout.getvalue()
            if printed_output:
                return printed_output.strip()
            
        except TimeoutError as e:
            logger.error(f"Code execution timed out: {str(e)}")
            raise
        except SyntaxError as e:
            logger.error(f"Syntax error during code execution: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during code execution: {str(e)}")
            raise
        finally:
            # Reset stdout
            sys.stdout = old_stdout
            signal.alarm(0)  # Disable the alarm

        return "No output produced."

    def output_data_analysis_parser(self, output: str, vision_llm:any,timeout: int = 2000, **output_kwargs: Any) -> str:
        """Process outputs in a default manner with a timeout."""
        if sys.version_info < (3, 9):
            logger.warning(
                "Python version must be >= 3.9 in order to use "
                "the default output processor, which executes "
                "the Python query. Instead, we will return the "
                "raw Python instructions as a string."
            )
            return output

        local_vars = {
            "df": self.df,
            "sns": sns,
            "plt": plt,
            "np": np,
            "pd": pd,
            "train_test_split": train_test_split,
            "X_train": self.X_train,
            "X_test": self.X_test,
            "y_train": self.y_train,
            "y_test": self.y_test,
            "import_model": self.import_model,
            "import_metric": self.import_metric,
            "show_plot": show_plot

        }
        global_vars = {}

        output = extract_python_codev4(output)
        
        # Redirect standard output to capture print statements
        old_stdout = sys.stdout
        sys.stdout = new_stdout = io.StringIO()
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            
            tree = ast.parse(output)
            module = ast.Module(body=tree.body[:-1], type_ignores=[])

            
            exec(compile(module, filename="<ast>", mode="exec"), {}, local_vars)  # type: ignore
            
            module_end = ast.Module(tree.body[-1:], type_ignores=[])
            module_end_str = ast.unparse(module_end)  # type: ignore
            
            if module_end_str.strip("'\"") != module_end_str:
                module_end_str = eval(module_end_str, global_vars, local_vars)
            

            try:
                
                output_str = str(eval(module_end_str, global_vars, local_vars))
                descriptions=[]
                for fig_num in plt.get_fignums(): 
                    plt.figure(fig_num)
                    descriptions.append(show_plotv2(vision_llm))
                    plt.close(fig_num)
                
                printed_output = new_stdout.getvalue()
          

                if printed_output:
                    output_str = printed_output + "\n" + output_str
                
                
                return output_str,descriptions

            except Exception:
                raise
        except TimeoutException:
            return "The execution timed out. Please try again with optimized code or increase the timeout limit."
        except Exception as e:
            err_string = (
                "There was an error running the output as Python code. "
                f"Error message: {e}"
            )
            traceback.print_exc()
            self.error_history.append({"error": str(e), "code": output})
            return err_string
        finally:
            sys.stdout = old_stdout  # Restore standard output
            signal.alarm(0)  # Disable the alarm