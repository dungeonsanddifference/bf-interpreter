import argparse
import os
import timeit

import numpy as np


def parse_code(raw: str) -> list[tuple[str, int]]:
    # Create an ir and collapse repeated operations
    ops = []
    last = None # last character
    count = 0 # count of consecutive characters

    for c in raw:
        if c not in "+-<>.,[]":
            continue
        
        if c == last:
            count += 1
        else:
            if last is not None:
                ops.append((last, count))
            last = c
            count = 1

    if last is not None:
        ops.append((last, count))

    return ops


def build_jump_table(code: list[tuple[str, int]]) -> dict[int, int]:
    """Build a jump table by parsing brackets using a stack"""
    table = {}
    stack = []

    for i, (c, _) in enumerate(code):
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


def run(ops: str, /, *, debug: bool = False) -> None:
    """Interpret a Brainf*** program in *file*."""
    tape: np.ndarray = np.zeros(30_000, dtype=np.uint8)
    ptr: int = 0
    jump_table: dict[int, int] = build_jump_table(ops)

    ip: int = 0
    while ip < len(ops):
        cmd, count = ops[ip]

        match cmd:
            case '>':
                ptr = (ptr + count) % len(tape)
            case '<':
                ptr = (ptr - count) % len(tape)
            case '+':
                tape[ptr] += count
            case '-':
                tape[ptr] -= count
            case ',':
                tape[ptr] = np.uint8(ord(input()[0])) # Only take first char
            case '.':
                print(chr(tape[ptr]) *  count, end='', flush=True)
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
        
        if debug:
            print(f"ip={ip}, cmd={cmd}, ptr={ptr}, tape[{ptr}]={tape[ptr]}")
        ip += 1
    
    
    if "zsh" in os.environ.get("SHELL", ""):
        # Suppress `%` prompt artifact in zsh
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Minimal Brainf**k interpreter with optional timing and debug output."
    )
    parser.add_argument("source", help="Path to Brainf**k source file")
    parser.add_argument(
        "-d", "--debug", action="store_true",
        help="print interpreter state after every instruction"
    )
    parser.add_argument(
        "-t", "--time", action="store_true",
        help="time execution with the built-in timeit module"
    )
    parser.add_argument(
        "-n", "--number", type=int, default=1000,
        help="number of repetitions to run when --time is given (default: 1000)"
    )
    args = parser.parse_args()

    # Load program
    with open(args.source, "r", encoding="utf-8") as f:
        program = parse_code(f.read())

    # Run or benchmark
    if args.time:
        seconds = timeit.timeit(
            lambda: run(program, debug=args.debug),
            number=args.number
        )
        print(f"{seconds:.6f} s for {args.number} runs "
              f"({seconds/args.number:.6f} s per run)")
    else:
        run(program, debug=args.debug)


if __name__ == "__main__":
    main()

    """
    $ uv run 02_batch.py example.bf --time -n 10000 
    3.504628 s for 10000 runs (0.000350 s per run)
    """