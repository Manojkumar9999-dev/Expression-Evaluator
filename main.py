#!/usr/bin/env python3
"""
Expression Evaluator with GUI (Tkinter)

Features:
- Parses and evaluates arithmetic expressions in infix form.
- Supports: +, -, *, /, ^ (power), parentheses, unary minus, decimals.
- Converts infix -> postfix (Shunting Yard) and evaluates postfix.
- Shows step-by-step postfix form and evaluation stack trace in the GUI.
- Basic error handling (syntax errors, division by zero).
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# --------------------------
# Tokenizer / Lexer
# --------------------------

def tokenize(expr: str):
    """
    Convert expression string into list of tokens.
    Tokens: numbers (ints/floats), operators, parentheses.
    Recognizes unary minus (as 'u-') during tokenization by context.
    """
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit() or ch == '.':
            num_chars = [ch]
            i += 1
            while i < n and (expr[i].isdigit() or expr[i] == '.'):
                num_chars.append(expr[i])
                i += 1
            num_str = ''.join(num_chars)
            # Validate number (at most one dot)
            if num_str.count('.') > 1:
                raise ValueError(f"Invalid numeric literal: {num_str}")
            tokens.append(num_str)
            continue
        # operators and parentheses
        if ch in '+-*/^()':
            # detect unary minus: if ch == '-' and either at start, or previous token is operator or '('
            if ch == '-':
                prev = tokens[-1] if tokens else None
                if prev is None or (prev in ('+', '-', '*', '/', '^', '(', 'u-')):
                    # unary minus token
                    tokens.append('u-')
                    i += 1
                    continue
            tokens.append(ch)
            i += 1
            continue
        # unsupported character
        raise ValueError(f"Unsupported character: '{ch}'")
    return tokens

# --------------------------
# Shunting Yard -> Infix to Postfix
# --------------------------

OPERATORS = {
    '+': {'prec': 2, 'assoc': 'L'},
    '-': {'prec': 2, 'assoc': 'L'},
    '*': {'prec': 3, 'assoc': 'L'},
    '/': {'prec': 3, 'assoc': 'L'},
    '^': {'prec': 4, 'assoc': 'R'},
    'u-': {'prec': 5, 'assoc': 'R'},  # unary minus: high precedence, right-assoc
}

def infix_to_postfix(tokens):
    """Shunting-yard algorithm. Returns list of postfix tokens."""
    output = []
    stack = []
    for tok in tokens:
        if is_number(tok):
            output.append(tok)
        elif tok in OPERATORS:
            o1 = tok
            while stack and stack[-1] in OPERATORS:
                o2 = stack[-1]
                p1 = OPERATORS[o1]['prec']
                p2 = OPERATORS[o2]['prec']
                if (OPERATORS[o1]['assoc'] == 'L' and p1 <= p2) or \
                   (OPERATORS[o1]['assoc'] == 'R' and p1 < p2):
                    output.append(stack.pop())
                else:
                    break
            stack.append(o1)
        elif tok == '(':
            stack.append(tok)
        elif tok == ')':
            # pop until '('
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched parentheses")
            stack.pop()  # remove '('
        else:
            raise ValueError(f"Unknown token in infix_to_postfix: {tok}")
    while stack:
        top = stack.pop()
        if top in ('(', ')'):
            raise ValueError("Mismatched parentheses")
        output.append(top)
    return output

# --------------------------
# Postfix Evaluation
# --------------------------

def evaluate_postfix(postfix_tokens):
    """Evaluate postfix expression. Returns (value, evaluation_trace)"""
    stack = []
    trace = []
    for tok in postfix_tokens:
        if is_number(tok):
            val = float(tok)
            stack.append(val)
            trace.append(f"PUSH {val}")
        elif tok in OPERATORS:
            if tok == 'u-':
                if not stack:
                    raise ValueError("Insufficient operands for unary minus")
                a = stack.pop()
                res = -a
                stack.append(res)
                trace.append(f"UNARY_MINUS {a} -> {res}")
            else:
                if len(stack) < 2:
                    raise ValueError(f"Insufficient operands for '{tok}'")
                b = stack.pop()
                a = stack.pop()
                res = apply_op(a, b, tok)
                stack.append(res)
                trace.append(f"{a} {tok} {b} -> {res}")
        else:
            raise ValueError(f"Unknown token in evaluate_postfix: {tok}")
    if len(stack) != 1:
        raise ValueError("The expression could not be evaluated to a single value (syntax error).")
    return stack[0], trace

def apply_op(a, b, op):
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        return a / b
    if op == '^':
        # power
        return math.pow(a, b)
    raise ValueError(f"Unsupported operator: {op}")

def is_number(token):
    try:
        float(token)
        return True
    except Exception:
        return False

# --------------------------
# High-level evaluate function
# --------------------------

def evaluate_expression(expr: str):
    """
    Full pipeline:
    1. Tokenize
    2. Infix -> Postfix
    3. Evaluate Postfix
    Returns: (value, tokens, postfix_tokens, trace)
    """
    tokens = tokenize(expr)
    postfix = infix_to_postfix(tokens)
    value, trace = evaluate_postfix(postfix)
    return value, tokens, postfix, trace

# --------------------------
# GUI (Tkinter)
# --------------------------

class ExpressionEvaluatorApp:
    def __init__(self, root):
        self.root = root
        root.title("Expression Evaluator")
        root.geometry("820x640")
        root.resizable(False, False)

        title = ttk.Label(root, text="Expression Evaluator", font=("Segoe UI", 16, "bold"))
        title.pack(pady=10)

        frm = ttk.Frame(root, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # Input
        input_lbl = ttk.Label(frm, text="Enter expression (infix):")
        input_lbl.grid(row=0, column=0, sticky=tk.W)
        self.input_var = tk.StringVar()
        self.entry = ttk.Entry(frm, textvariable=self.input_var, font=("Consolas", 12), width=70)
        self.entry.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0,10))
        self.entry.bind("<Return>", lambda e: self.evaluate())

        # Buttons
        eval_btn = ttk.Button(frm, text="Evaluate", command=self.evaluate)
        eval_btn.grid(row=2, column=0, sticky=tk.W, padx=(0,10))
        clear_btn = ttk.Button(frm, text="Clear", command=self.clear_all)
        clear_btn.grid(row=2, column=1, sticky=tk.W)
        sample_btn = ttk.Button(frm, text="Insert Sample", command=self.insert_sample)
        sample_btn.grid(row=2, column=2, sticky=tk.W, padx=(10,0))

        # Output areas
        out_frame = ttk.Frame(frm)
        out_frame.grid(row=3, column=0, columnspan=3, pady=12, sticky=tk.NSEW)

        # Postfix
        postfix_lbl = ttk.Label(out_frame, text="Postfix (RPN):")
        postfix_lbl.grid(row=0, column=0, sticky=tk.W)
        self.postfix_box = scrolledtext.ScrolledText(out_frame, height=4, width=90, font=("Consolas", 11))
        self.postfix_box.grid(row=1, column=0, pady=(0,10))

        # Result
        result_lbl = ttk.Label(out_frame, text="Result:")
        result_lbl.grid(row=2, column=0, sticky=tk.W)
        self.result_var = tk.StringVar()
        self.result_entry = ttk.Entry(out_frame, textvariable=self.result_var, font=("Consolas", 12), width=40, state="readonly")
        self.result_entry.grid(row=3, column=0, sticky=tk.W, pady=(0,10))

        # Trace
        trace_lbl = ttk.Label(out_frame, text="Evaluation Trace (stack operations):")
        trace_lbl.grid(row=4, column=0, sticky=tk.W)
        self.trace_box = scrolledtext.ScrolledText(out_frame, height=10, width=90, font=("Consolas", 11))
        self.trace_box.grid(row=5, column=0, pady=(0,10))

        # History
        hist_lbl = ttk.Label(out_frame, text="History:")
        hist_lbl.grid(row=6, column=0, sticky=tk.W)
        self.history_box = scrolledtext.ScrolledText(out_frame, height=6, width=90, font=("Consolas", 11))
        self.history_box.grid(row=7, column=0, pady=(0,10))
        self.history_box.configure(state='disabled')

        # Status
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(fill=tk.X, side=tk.BOTTOM)

        # Sample list
        self.samples = [
            "3 + 4 * 2 / (1 - 5) ^ 2 ^ 3",
            "-3 + 4 * (2 - 1)",
            "2^3^2",
            " ( 3.5 + 2.1 ) * 4 - -2 ",
            "10 / (5-5)",
            "3 + + 4",  # invalid
        ]

    def insert_sample(self):
        # cycle through samples
        cur = self.input_var.get().strip()
        try:
            idx = self.samples.index(cur)
            idx = (idx + 1) % len(self.samples)
        except ValueError:
            idx = 0
        self.input_var.set(self.samples[idx])

    def clear_all(self):
        self.input_var.set("")
        self.postfix_box.delete("1.0", tk.END)
        self.result_var.set("")
        self.trace_box.delete("1.0", tk.END)

    def evaluate(self):
        expr = self.input_var.get()
        if not expr.strip():
            messagebox.showinfo("Input needed", "Please enter an expression to evaluate.")
            return
        try:
            val, tokens, postfix, trace = evaluate_expression(expr)
            # display postfix as space-separated
            postfix_str = ' '.join(postfix)
            self.postfix_box.delete("1.0", tk.END)
            self.postfix_box.insert(tk.END, postfix_str)
            # display result
            # if integer-equivalent, show as int
            if abs(val - round(val)) < 1e-12:
                display_val = str(int(round(val)))
            else:
                display_val = str(val)
            self.result_var.set(display_val)
            # trace
            self.trace_box.delete("1.0", tk.END)
            for line in trace:
                self.trace_box.insert(tk.END, line + "\n")
            # append to history
            self.append_history(expr, postfix_str, display_val)
            self.status_var.set("Evaluated successfully")
        except ZeroDivisionError as zde:
            messagebox.showerror("Math error", f"Evaluation error: {zde}")
            self.status_var.set("Error: Division by zero")
        except Exception as e:
            messagebox.showerror("Error", f"Could not evaluate expression:\n{e}")
            self.status_var.set(f"Error: {e}")

    def append_history(self, expr, postfix, result):
        self.history_box.configure(state='normal')
        self.history_box.insert(tk.END, f"> {expr}\n  Postfix: {postfix}\n  Result: {result}\n\n")
        self.history_box.configure(state='disabled')

def main():
    root = tk.Tk()
    app = ExpressionEvaluatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
