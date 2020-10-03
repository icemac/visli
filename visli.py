"""Cut video files into slices.

Requires ffmpeg to be installed.
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


parser = argparse.ArgumentParser(usage="python visli.py", description=__doc__)
parser.add_argument('input', action="store", help="input file")
parser.add_argument('-d', action="store", type=int, default=15,
                    help="duration of slices in minutes")

args = parser.parse_args()
input = pathlib.Path(args.input)
duration_in_min = args.d
duration_hms = to_hms(duration_in_min * 60)

# Taken from https://superuser.com/a/945604
lenght_in_s = int(float(call(
    'ffprobe',
    '-v', 'error',
    '-show_entries', 'format=duration',
    '-of', 'default=noprint_wrappers=1:nokey=1',
    input)))

slice_starts = [
    to_hms(x) for x in range(0, lenght_in_s, (duration_in_min * 60 - 30))]

for index, start in enumerate(slice_starts, 1):
    output = input.parents[0] / f'{input.stem}-{index}{input.suffix}'
    # Taken from https://www.arj.no/2018/05/18/trimvideo/
    call(
        'ffmpeg',
        '-i', input,
        '-ss', start,
        '-t', duration_hms,
        '-c:v', 'copy',
        '-c:a', 'copy',
        output
    )

