#!/usr/bin/env python3
"""Auto Mix & Master — command line.

  python cli.py master in.wav out.wav --lufs -14 --tp -1
  python cli.py analyze in.wav
"""
import argparse
import sys
from engine import master, analyze, EngineError


def main() -> int:
    p = argparse.ArgumentParser(description="Auto mix & master")
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("master", help="master a track to a loudness target")
    m.add_argument("input")
    m.add_argument("output")
    m.add_argument("--lufs", type=float, default=-14.0, help="target integrated loudness (default -14)")
    m.add_argument("--tp", type=float, default=-1.0, help="max true peak dBTP (default -1)")

    a = sub.add_parser("analyze", help="report loudness/peak of a track")
    a.add_argument("input")

    args = p.parse_args()
    try:
        if args.cmd == "master":
            before = analyze(args.input)
            res = master(args.input, args.output, target_lufs=args.lufs, true_peak=args.tp)
            after = analyze(args.output)
            print("— before —"); print(before.pretty())
            print("\n— after —"); print(after.pretty())
            print(f"\n✓ Mastered → {res.output}")
        elif args.cmd == "analyze":
            print(analyze(args.input).pretty())
    except EngineError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
