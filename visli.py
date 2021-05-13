OVERLAP_IN_S = 30
FACTOR_LAST_SLICE = 1.5

doc = f"""Cut video files into slices.

Each slice has an overlap of {OVERLAP_IN_S} seconds with the previous one.
The last slice is sized up to {FACTOR_LAST_SLICE} times of the other slices to
prevent having a tiny last slice.

Requires Python 3.8+ and ffmpeg to be installed.
"""

from datetime import timedelta
import argparse
import pathlib
import subprocess


def call(*args):
    """Call args in shell and return stdout."""
    result = subprocess.run(args, capture_output=True)
    result.check_returncode()
    return result.stdout


def to_hms(seconds):
    """Convert number of seconds to HH:MM:SS."""
    return str(timedelta(seconds=seconds))


parser = argparse.ArgumentParser(usage="python visli.py", description=doc)
parser.add_argument('input', action="store", nargs='+',
                    help="input file(s), multiple times possible")
parser.add_argument('-d', metavar='n', action="store", type=int, default=15,
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
    slice_starts_in_s = [
        x for x in range(0, lenght_in_s, (duration_in_s - OVERLAP_IN_S))]

    slice_starts_in_hms = [to_hms(x) for x in slice_starts_in_s]
    print(f'Processing {input.name} ...')
    call_break = False
    for num, start_in_hms in enumerate(slice_starts_in_hms, 1):
        current_start_in_s = slice_starts_in_s[num - 1]
        remaining_in_s = lenght_in_s - current_start_in_s
        if remaining_in_s < duration_in_s * FACTOR_LAST_SLICE:
            duration_in_hms = to_hms(remaining_in_s)
            call_break = True
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
        if call_break:
            break
