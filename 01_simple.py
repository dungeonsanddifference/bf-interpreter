import argparse
import os
import timeit

import numpy as np


def parse_code(raw: str) -> str:
    return "".join(c for c in raw if c in "+-<>.,[]")


def build_jump_table(code: str) -> dict[int, int]:
    table, stack = {}, []
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


def run(code: str, /, *, debug: bool = False) -> None:
    """Interpret a Brainf*** program in *file*."""
    tape = np.zeros(30_000, dtype=np.uint8)
    ptr = ip = 0
    jump_table = build_jump_table(code)

    while ip < len(code):
        cmd = code[ip]
        match cmd:
            case '>':
                ptr = (ptr + 1) % tape.size
            case '<':
                ptr = (ptr - 1) % tape.size
            case '+':
                tape[ptr] += 1
            case '-':
                tape[ptr] -= 1
            case ',':
                tape[ptr] = np.uint8(ord(input()[0]))
            case '.':
                print(chr(tape[ptr]), end='', flush=True)
            case '[':
                if tape[ptr] == 0:
                    ip = jump_table[ip]
                    continue
            case ']':
                if tape[ptr] != 0:
                    ip = jump_table[ip]
                    continue
        if debug:
            print(f"ip={ip:05}, cmd={cmd}, ptr={ptr:05}, tape[{ptr}]={tape[ptr]}")
        ip += 1

    # Suppress the stray '%' that z-shell prints after a program with no newline
    if "zsh" in os.environ.get("SHELL", ""):
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
    $ uv run 01_simple.py example.bf --time -n 10000
    4.883669 s for 10000 runs (0.000488 s per run)
    """
