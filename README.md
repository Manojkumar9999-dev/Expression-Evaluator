# Expression Evaluator

A compact Expression Evaluator implemented in Python with a Tkinter GUI.

## Features
- Parse and evaluate infix arithmetic expressions.
- Operators supported: `+`, `-`, `*`, `/`, `^` (power), parentheses `(` `)`.
- Supports unary minus (e.g., `-3`, `2 * -5`) and decimal numbers.
- Shows conversion to Postfix (Reverse Polish Notation) and a step-by-step evaluation trace.
- Implemented from scratch (no parsing libraries used).

## Files
- `main.py` — main application (GUI + evaluator).
- `README.md` — this file.

## How it works (high level)
1. **Tokenize** the infix expression into numbers, operators, and parentheses.
2. **Convert** infix tokens to **postfix** using the **Shunting-yard algorithm**.
3. **Evaluate** postfix expression using a stack.
4. Display postfix, result, and evaluation trace in the GUI.

