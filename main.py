import os
import sys
import numpy as np

DEBUG = False


def parse_code(raw):
    return "".join([c for c in raw if c in "+-<>.,[]"])


def build_jump_table(code: str) -> dict[int, int]:
    """Build a jump table by parsing brackets using a stack"""
    table = {}
    stack = []

    for i, c in enumerate(code):
        if c == "[":
            stack.append(i)
        elif c == "]":
            if not stack:
                raise SyntaxError(f"Unmatched ] at position {i}")
            open_idx = stack.pop()
            table[open_idx] = i
            table[i] = open_idx

    if stack:
        raise SyntaxError(f"Unmatched [ at position {stack.pop()}")

    return table


def main(file):
    with open(file, "r") as f:
        raw: str = f.read()
    code: str = parse_code(raw)

    tape: np.ndarray = np.zeros(30_000, dtype=np.uint8)
    ptr: int = 0

    jump_table: dict[int, int] = build_jump_table(code)

    ip: int = 0
    while ip < len(code):
        cmd = code[ip]

        match cmd:
            case '>':
                ptr = (ptr + 1) % len(tape)
            case '<':
                ptr = (ptr - 1) % len(tape)
            case '+':
                tape[ptr] += 1
            case '-':
                tape[ptr] -= 1
            case ',':
                tape[ptr] = np.uint8(ord(input()[0])) # Only take first char
            case '.':
                print(chr(tape[ptr]), end='', flush=True)
            case '[':
                if tape[ptr] == 0:
                    ip = jump_table[ip] # skip execution
                    continue
            case ']':
                if tape[ptr] != 0:
                    ip = jump_table[ip] # return to start of loop
                    continue
            case _:
                # Should never get here
                raise RuntimeError(f"Invalid instruction: {cmd}")
        
        if DEBUG:
            print(f"ip={ip}, cmd={cmd}, ptr={ptr}, tape[{ptr}]={tape[ptr]}")
        ip += 1
    
    
    if "zsh" in os.environ.get("SHELL", ""):
        # Suppress `%` prompt artifact in zsh
        print()

if __name__ == "__main__":
    main(sys.argv[1])
