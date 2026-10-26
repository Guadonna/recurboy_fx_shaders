#!/usr/bin/env python3
"""Log Raspberry Pi health; optionally pause the explicitly selected recurBOY PID.
This is a CPU-side guard, not an FPS meter or a guarantee about chip temperature.
"""
import argparse
import csv
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def temperature():
    return int(Path('/sys/class/thermal/thermal_zone0/temp').read_text()) / 1000.0


def throttled():
    result = subprocess.check_output(['vcgencmd', 'get_throttled'], text=True, timeout=3)
    return int(result.strip().split('=')[1], 16)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pid', type=int, help='Pause this recurBOY process at the limit; verify the PID first')
    p.add_argument('--limit', type=float, default=70.0, help='Conservative operating limit in C (default 70)')
    p.add_argument('--duration', type=float, default=1800, help='Seconds to monitor; 0 means until Ctrl-C')
    args = p.parse_args()
    if not 40 <= args.limit <= 75 or args.duration < 0:
        p.error('Use a limit between 40 and 75 C and nonnegative duration')
    process = None
    if args.pid:
        process = Path('/proc') / str(args.pid)
        if process.joinpath('comm').read_text().strip().lower() != 'recurboy':
            p.error('--pid must identify recurBOY')
        identity = process.joinpath('stat').read_text().rsplit(')', 1)[1].split()[19]
        os.kill(args.pid, 0)
    writer = csv.writer(sys.stdout)
    writer.writerow(['elapsed_s', 'temperature_c', 'throttled_hex', 'action'])
    start = time.monotonic()
    while True:
        try:
            temp, flags = temperature(), throttled()
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            print('Health measurement failed: ' + str(error), file=sys.stderr)
            # Missing telemetry cannot establish safety. Stop guarded work.
            temp, flags = None, None
        alarm = temp is None or temp >= args.limit or bool(flags & 0xF)
        action = 'ALARM' if alarm else 'ok'
        if process:
            try:
                current = process.joinpath('stat').read_text().rsplit(')', 1)[1].split()[19]
            except FileNotFoundError:
                return 0
            if current != identity:
                raise RuntimeError('PID was reused; refusing to signal another process')
            if alarm:
                os.kill(args.pid, signal.SIGSTOP)
                action = 'PAUSED'
        writer.writerow([round(time.monotonic()-start, 2), temp,
                         hex(flags) if flags is not None else 'unknown', action])
        sys.stdout.flush()
        if alarm:
            if process:
                print('recurBOY paused. After cooling and correcting the cause, resume explicitly with: '
                      + 'kill -CONT ' + str(args.pid), file=sys.stderr)
            else:
                print('Disable FX and correct cooling/power. Monitor-only mode cannot pause the app.', file=sys.stderr)
            return 2
        if args.duration and time.monotonic()-start >= args.duration:
            return 0
        time.sleep(1)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
