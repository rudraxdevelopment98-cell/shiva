#!/usr/bin/env python3
"""Auto Mix & Master — command line.

  python cli.py master in.wav out.wav --lufs -14 --tp -1
  python cli.py analyze in.wav
"""
import argparse
import sys
from engine import master, analyze, automix, match, EngineError


def main() -> int:
    p = argparse.ArgumentParser(description="Auto mix & master")
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("master", help="master a track to a loudness target")
    m.add_argument("input")
    m.add_argument("output")
    m.add_argument("--lufs", type=float, default=-14.0, help="target integrated loudness (default -14)")
    m.add_argument("--tp", type=float, default=-1.0, help="max true peak dBTP (default -1)")
    m.add_argument("--preset", choices=["clean", "warm", "bright", "loud"], default=None,
                   help="optional tonal/dynamics chain (needs pedalboard)")

    x = sub.add_parser("mix", help="auto-mix 2+ stems into a mastered track")
    x.add_argument("stems", nargs="+", help="stem files (drums, bass, vocals, …)")
    x.add_argument("-o", "--output", required=True, help="output file")
    x.add_argument("--lufs", type=float, default=-14.0, help="final loudness target (default -14)")
    x.add_argument("--tp", type=float, default=-1.0, help="max true peak dBTP (default -1)")
    x.add_argument("--preset", choices=["clean", "warm", "bright", "loud"], default=None,
                   help="optional tonal/dynamics chain on the bus (needs pedalboard)")

    r = sub.add_parser("match", help="make a track sound like a reference song")
    r.add_argument("target", help="your track")
    r.add_argument("reference", help="the song to match")
    r.add_argument("-o", "--output", required=True, help="output file")

    a = sub.add_parser("analyze", help="report loudness/peak of a track")
    a.add_argument("input")

    args = p.parse_args()
    try:
        if args.cmd == "master":
            before = analyze(args.input)
            res = master(args.input, args.output, target_lufs=args.lufs,
                         true_peak=args.tp, preset=args.preset)
            after = analyze(args.output)
            print("— before —"); print(before.pretty())
            print("\n— after —"); print(after.pretty())
            print(f"\n✓ Mastered → {res.output}" + (f"  (preset: {res.preset})" if res.preset else ""))
        elif args.cmd == "mix":
            res = automix(args.stems, args.output, target_lufs=args.lufs,
                          true_peak=args.tp, preset=args.preset)
            after = analyze(args.output)
            print(f"mixed {res.stems} stems →")
            print(after.pretty())
            print(f"\n✓ Mix master → {res.output}" + (f"  (preset: {res.preset})" if res.preset else ""))
        elif args.cmd == "match":
            res = match(args.target, args.reference, args.output)
            print(analyze(args.output).pretty())
            print(f"\n✓ Matched to reference → {res.output}")
        elif args.cmd == "analyze":
            print(analyze(args.input).pretty())
    except EngineError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
