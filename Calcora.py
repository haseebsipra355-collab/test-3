# ================================================
# ✨ UNIQUE PYTHON CALCULATOR - "Calcora" ✨
# A smart, beautiful, and feature-rich calculator
# Features:
#   • Natural language + math expression support
#   • Memory (ans, variables)
#   • History with navigation
#   • Scientific functions
#   • Colorful terminal UI
#   • Error handling & helpful messages
# ================================================

import math
import re
from datetime import datetime

# ANSI Colors for beautiful UI
class Colors:
    HEADER = '\033[95m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

class Calcora:
    def __init__(self):
        self.history = []
        self.memory = {"ans": 0}
        self.variables = {}
        print(Colors.HEADER + "\n" + "="*55)
        print(" " * 18 + "🚀 CALCORA v2.0" + " " * 18)
        print("="*55 + Colors.RESET)
        print(Colors.CYAN + "Type 'help' for commands | 'quit' to exit\n" + Colors.RESET)

    def show_help(self):
        print(Colors.YELLOW + """
Available Commands:
  help      → Show this help
  history   → Show calculation history
  clear     → Clear screen & history
  vars      → Show saved variables
  del x     → Delete variable 'x'
  quit/exit → Close calculator

Examples:
  25 + 17 * 3
  sin(30) + log(100)
  2 ** 8
  ans + 50
  radius = 5; pi * radius ** 2
        """ + Colors.RESET)

    def evaluate(self, expr):
        try:
            # Replace common natural language
            expr = expr.lower().replace("plus", "+").replace("minus", "-") \
                         .replace("times", "*").replace("multiplied by", "*") \
                         .replace("divided by", "/").replace("to the power", "**")

            # Support for variables and ans
            for var, val in {**self.variables, **self.memory}.items():
                expr = re.sub(rf'\b{var}\b', str(val), expr)

            # Safe evaluation with limited math functions
            allowed_names = {
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "asin": math.asin, "acos": math.acos, "atan": math.atan,
                "log": math.log, "log10": math.log10, "sqrt": math.sqrt,
                "pi": math.pi, "e": math.e, "abs": abs, "round": round,
                "floor": math.floor, "ceil": math.ceil, "pow": pow
            }

            # Evaluate safely
            result = eval(expr, {"__builtins__": {}}, allowed_names)
            
            # Store result
            self.memory["ans"] = result
            return result

        except Exception as e:
            return f"{Colors.RED}Error: {str(e)}{Colors.RESET}"

    def run(self):
        while True:
            try:
                user_input = input(Colors.BOLD + "➤ " + Colors.RESET).strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ["quit", "exit"]:
                    print(Colors.GREEN + "\n👋 Goodbye! Thanks for using Calcora.\n" + Colors.RESET)
                    break

                elif user_input.lower() == "help":
                    self.show_help()
                    continue

                elif user_input.lower() == "history":
                    if not self.history:
                        print(Colors.YELLOW + "No history yet." + Colors.RESET)
                    else:
                        for i, (time, expr, res) in enumerate(self.history[-10:], 1):
                            print(f"{Colors.CYAN}{i:2d}.{Colors.RESET} [{time}] {expr} = {Colors.GREEN}{res}{Colors.RESET}")
                    continue

                elif user_input.lower() == "clear":
                    print("\033c", end="")
                    self.history.clear()
                    print(Colors.GREEN + "Screen and history cleared." + Colors.RESET)
                    continue

                elif user_input.lower() == "vars":
                    if not self.variables:
                        print(Colors.YELLOW + "No variables saved." + Colors.RESET)
                    else:
                        for var, val in self.variables.items():
                            print(f"  {Colors.BOLD}{var}{Colors.RESET} = {Colors.GREEN}{val}{Colors.RESET}")
                    continue

                elif user_input.startswith("del "):
                    var = user_input[4:].strip()
                    if var in self.variables:
                        del self.variables[var]
                        print(Colors.GREEN + f"Variable '{var}' deleted." + Colors.RESET)
                    else:
                        print(Colors.RED + f"Variable '{var}' not found." + Colors.RESET)
                    continue

                # Support assignment: x = expression
                if "=" in user_input and not re.search(r'==|>=|<=|!=', user_input):
                    var, expr = [x.strip() for x in user_input.split("=", 1)]
                    if var.isidentifier():
                        result = self.evaluate(expr)
                        if not isinstance(result, str) or "Error" not in result:
                            self.variables[var] = result
                            print(f"{Colors.GREEN}✓ {var} = {result}{Colors.RESET}")
                            self.history.append((datetime.now().strftime("%H:%M:%S"), user_input, result))
                            continue

                # Normal calculation
                result = self.evaluate(user_input)
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                if isinstance(result, (int, float)):
                    print(f"{Colors.GREEN}→ {result}{Colors.RESET}")
                    self.history.append((timestamp, user_input, result))
                else:
                    print(result)

            except KeyboardInterrupt:
                print(Colors.RED + "\n\nCtrl+C detected. Type 'quit' to exit." + Colors.RESET)
            except Exception as e:
                print(Colors.RED + f"Unexpected error: {e}" + Colors.RESET)


# ====================== RUN THE CALCULATOR ======================
if __name__ == "__main__":
    calculator = Calcora()
    calculator.run()