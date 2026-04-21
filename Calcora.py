# ================================================
# ✨ CALCORA v2.1 - Smart Terminal Calculator ✨
# ================================================

import math
import re
import ast
import json
from datetime import datetime
from pathlib import Path

# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class Calcora:
    def __init__(self):
        self.history = []
        self.memory = {"ans": 0.0}
        self.variables = {}
        self.use_degrees = False  # Toggle for trig functions
        self.history_file = Path("calcora_history.txt")

        self.load_history()
        self.print_banner()

    def print_banner(self):
        print(Colors.HEADER + "\n" + "="*60)
        print(" " * 20 + "🚀 CALCORA v2.1" + " " * 20)
        print("="*60 + Colors.RESET)
        print(Colors.CYAN + "Type 'help' for commands | 'quit' to exit\n" + Colors.RESET)

    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    for line in f.readlines()[-20:]:  # last 20 entries
                        self.history.append(json.loads(line.strip()))
            except:
                pass

    def save_history_entry(self, entry):
        try:
            with open(self.history_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except:
            pass

    def show_help(self):
        print(Colors.YELLOW + """
Commands:
  help          → Show this help
  history       → Show last calculations
  clear         → Clear screen & current session history
  vars          → Show saved variables
  del x         → Delete variable
  deg / rad     → Toggle degrees or radians
  quit / exit   → Exit

Examples:
  25 + 17 * 3
  sin(30) + log(100)
  2^8 or 2**8
  radius = 5; pi * radius ** 2
  ans + 50
  5! + sqrt(16)
        """ + Colors.RESET)

    def safe_eval(self, expr: str):
        """Safer evaluation using AST"""
        try:
            # Clean and normalize expression
            expr = expr.strip().lower()
            expr = expr.replace('^', '**').replace('x', '*')

            # Replace natural language
            replacements = {
                'plus': '+', 'minus': '-', 'times': '*', 'multiplied by': '*',
                'divided by': '/', 'to the power': '**', 'squared': '**2',
                'cubed': '**3'
            }
            for word, op in replacements.items():
                expr = expr.replace(word, op)

            # Replace variables and ans
            context = {**self.variables, **self.memory}
            for var, val in context.items():
                expr = re.sub(rf'\b{var}\b', str(val), expr)

            # Parse safely
            tree = ast.parse(expr, mode='eval')
            allowed = {
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "asin": math.asin, "acos": math.acos, "atan": math.atan,
                "log": math.log, "log10": math.log10, "log2": math.log2,
                "sqrt": math.sqrt, "exp": math.exp,
                "pi": math.pi, "e": math.e,
                "abs": abs, "round": round,
                "floor": math.floor, "ceil": math.ceil,
                "factorial": math.factorial, "pow": pow
            }

            def eval_node(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    left = eval_node(node.left)
                    right = eval_node(node.right)
                    if isinstance(node.op, ast.Add): return left + right
                    if isinstance(node.op, ast.Sub): return left - right
                    if isinstance(node.op, ast.Mult): return left * right
                    if isinstance(node.op, ast.Div): return left / right
                    if isinstance(node.op, ast.Pow): return left ** right
                elif isinstance(node, ast.UnaryOp):
                    operand = eval_node(node.operand)
                    if isinstance(node.op, ast.USub): return -operand
                elif isinstance(node, ast.Call):
                    func_name = node.func.id
                    if func_name in allowed:
                        args = [eval_node(arg) for arg in node.args]
                        func = allowed[func_name]
                        if func_name in ["sin", "cos", "tan"] and self.use_degrees:
                            args[0] = math.radians(args[0])
                        return func(*args)
                elif isinstance(node, ast.Name):
                    if node.id in allowed:
                        return allowed[node.id]
                    raise NameError(f"Unknown name: {node.id}")
                return node

            result = eval_node(tree.body)
            return result

        except Exception as e:
            return f"Error: {str(e)}"

    def format_result(self, result):
        if isinstance(result, float):
            if abs(result) > 1e10 or abs(result) < 1e-8:
                return f"{result:.6e}"
            elif result == int(result):
                return str(int(result))
            else:
                return f"{result:.8g}"
        return str(result)

    def run(self):
        while True:
            try:
                user_input = input(Colors.BOLD + "➤ " + Colors.RESET).strip()
                if not user_input:
                    continue

                cmd = user_input.lower()

                if cmd in ["quit", "exit"]:
                    print(Colors.GREEN + "\n👋 Goodbye! See you next time.\n" + Colors.RESET)
                    break

                elif cmd == "help":
                    self.show_help()
                    continue

                elif cmd == "history":
                    if not self.history:
                        print(Colors.YELLOW + "No history yet." + Colors.RESET)
                    else:
                        for i, (time, expr, res) in enumerate(self.history[-15:], 1):
                            print(f"{Colors.CYAN}{i:2d}.{Colors.RESET} [{time}] {expr} = {Colors.GREEN}{res}{Colors.RESET}")
                    continue

                elif cmd == "clear":
                    print("\033c", end="")
                    self.history.clear()
                    print(Colors.GREEN + "✓ Screen and session history cleared." + Colors.RESET)
                    continue

                elif cmd == "vars":
                    if not self.variables:
                        print(Colors.YELLOW + "No variables saved yet." + Colors.RESET)
                    else:
                        for var, val in self.variables.items():
                            print(f"  {Colors.BOLD}{var}{Colors.RESET} = {Colors.GREEN}{val}{Colors.RESET}")
                    continue

                elif cmd.startswith("del "):
                    var = cmd[4:].strip()
                    if var in self.variables:
                        del self.variables[var]
                        print(Colors.GREEN + f"✓ Variable '{var}' deleted." + Colors.RESET)
                    else:
                        print(Colors.RED + f"✗ Variable '{var}' not found." + Colors.RESET)
                    continue

                elif cmd in ["deg", "degrees"]:
                    self.use_degrees = True
                    print(Colors.GREEN + "✓ Trigonometric functions now in Degrees" + Colors.RESET)
                    continue
                elif cmd in ["rad", "radians"]:
                    self.use_degrees = False
                    print(Colors.GREEN + "✓ Trigonometric functions now in Radians" + Colors.RESET)
                    continue

                # Variable assignment: x = expression
                if "=" in user_input and not re.search(r'==|>=|<=|!=|=>', user_input):
                    var, expr = [x.strip() for x in user_input.split("=", 1)]
                    if var.isidentifier() and var not in ["ans", "pi", "e"]:
                        result = self.safe_eval(expr)
                        if not isinstance(result, str) or "Error" not in result:
                            self.variables[var] = result
                            print(f"{Colors.GREEN}✓ {var} = {self.format_result(result)}{Colors.RESET}")
                            entry = (datetime.now().strftime("%H:%M:%S"), user_input, self.format_result(result))
                            self.history.append(entry)
                            self.save_history_entry(entry)
                            continue

                # Normal calculation
                result = self.safe_eval(user_input)
                timestamp = datetime.now().strftime("%H:%M:%S")

                if isinstance(result, (int, float)):
                    formatted = self.format_result(result)
                    print(f"{Colors.GREEN}→ {formatted}{Colors.RESET}")
                    self.memory["ans"] = result

                    entry = (timestamp, user_input, formatted)
                    self.history.append(entry)
                    self.save_history_entry(entry)
                else:
                    print(Colors.RED + result + Colors.RESET)

            except KeyboardInterrupt:
                print(Colors.RED + "\n\nCtrl+C detected. Type 'quit' to exit." + Colors.RESET)
            except Exception as e:
                print(Colors.RED + f"Unexpected error: {e}" + Colors.RESET)


# ====================== RUN ======================
if __name__ == "__main__":
    try:
        calculator = Calcora()
        calculator.run()
    except Exception as e:
        print(Colors.RED + f"Fatal error: {e}" + Colors.RESET)