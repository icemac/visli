OVERLAP_IN_S = 30
FACTOR_LAST_SLICE = 1.5

doc = f"""Cut video files into slices.

Each slice has an overlap of {OVERLAP_IN_S} seconds with the previous one.
The last slice is sized up to {FACTOR_LAST_SLICE} times of the other slices to
prevent having a tiny last slice.

Requires Python 3.9+ and ffmpeg to be installed.
"""

from datetime import timedelta
from typing import Iterator, Tuple
import argparse
import pathlib
import subprocess


def call(*args) -> bytes:
    """Call args in shell and return stdout."""
    result = subprocess.run(args, capture_output=True)
    result.check_returncode()
    return result.stdout


def to_hms(seconds: float) -> str:
    """Convert number of seconds to HH:MM:SS."""
    return str(timedelta(seconds=seconds))


def slices(
    overall_lenght_in_s: int,
    default_slice_lenght_in_s: int,
) -> Iterator[Tuple[float, float]]:
    """Cut into slices returning a list of (pos, duration) tuples."""
    pos: float = 0.0
    max_slice_len = default_slice_lenght_in_s * FACTOR_LAST_SLICE
    while pos <= overall_lenght_in_s:
        if pos + max_slice_len >= overall_lenght_in_s:
            yield (pos, float(overall_lenght_in_s - pos))
            pos += max_slice_len
        else:
            yield (pos, default_slice_lenght_in_s)
            pos += default_slice_lenght_in_s - OVERLAP_IN_S


if __name__ == '__main__':

    parser = argparse.ArgumentParser(usage="python visli.py", description=doc)
    parser.add_argument(
        'input', action="store", nargs='+',
        help="input file(s), multiple times possible")
    parser.add_argument(
        '-d', metavar='n', action="store", type=int, default=15,
        help="duration of slices in minutes, default: 15")

    args = parser.parse_args()
    input_paths = [pathlib.Path(x) for x in args.input]
    duration_in_min = args.d
    duration_in_s = duration_in_min * 60
    duration_in_hms = to_hms(duration_in_min * 60)

    for input in input_paths:
        # Taken from https://superuser.com/a/945604
        lenght_in_s = int(float(call(
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input)))

        print(f'Processing {input.name} ...')
        for num, (start_in_s, duration_in_s) in enumerate(
                slices(lenght_in_s, duration_in_s), 1):
            start_in_hms = to_hms(start_in_s)
            duration_in_hms = to_hms(duration_in_s)
            output = input.parents[0] / f'{input.stem}-{num}{input.suffix}'
            # Taken from https://www.arj.no/2018/05/18/trimvideo/
            call(
                'ffmpeg',
                '-i', input,
                '-ss', start_in_hms,
                '-t', duration_in_hms,
                '-c:v', 'copy',
                '-c:a', 'copy',
                output
            )
