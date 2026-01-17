import json
import os
import sys
import time
from pathlib import Path

import click
import numpy as np
import pyopencl as cl
from base58 import alphabet, b58encode

# Fixed-size buffers (tune based on GPU memory)
MAX_MATCHES = 256
RESULT_SIZE = MAX_MATCHES * 64  # 64 bytes per private key


def select_device():
    available_platforms = cl.get_platforms()
    if len(available_platforms) == 0:
        click.echo("No OpenCL platforms found", err=True)
        exit(1)

    # select platform
    while True:
        if "GRIND_PLATFORM_IDX" in os.environ:
            platform_idx = int(os.environ["GRIND_PLATFORM_IDX"])
        else:
            for idx, selected_platform in enumerate(available_platforms):
                click.echo(f"[{idx}] {selected_platform.name}")

            platform_idx = click.prompt("Select platform", type=click.INT, default=0)
            click.echo(f"Set GRIND_PLATFORM_IDX={platform_idx} environment variable to skip this prompt")

        if platform_idx < 0 or platform_idx >= len(available_platforms):
            click.echo("Invalid platform", err=True)
            continue

        selected_platform = available_platforms[platform_idx]
        break

    available_devices = selected_platform.get_devices()
    if len(available_devices) == 0:
        click.echo("No OpenCL devices found for selected platform", err=True)
        exit(1)

    # select device
    while True:
        if "GRIND_DEVICE_IDX" in os.environ:
            device_idx = int(os.environ["GRIND_DEVICE_IDX"])
        else:
            for idx, selected_device in enumerate(available_devices):
                click.echo(f"[{idx}] {selected_device.name}")

            device_idx = click.prompt("Select device", type=click.INT, default=0)
            click.echo(f"Set GRIND_DEVICE_IDX={device_idx} environment variable to skip this prompt")

        if device_idx < 0 or device_idx >= len(available_devices):
            click.echo("Invalid device", err=True)
            continue

        return available_devices[device_idx]


def initiate_context(device):
    ctx = cl.Context([device])
    queue = cl.CommandQueue(ctx)

    return ctx, queue


def format_rate(speed):
    unites = ["H/s", "KH/s", "MH/s", "GH/s", "TH/s"]

    for i in range(len(unites)):
        if speed < 1000:
            return f"{speed:.2f} {unites[i]}"
        speed /= 1000

    return f"{speed:.2f} {unites[-1]}"


def format_elapsed(secs):
    hours = int(secs // 3600)
    minutes = int((secs % 3600) // 60)
    seconds = int(secs % 60)

    return f"{hours:d}h{minutes:02d}m{seconds:02d}s"


def print_message(match_mode=0, word="", limit=1):
    match_type = ""
    match match_mode:
        case 0 | 1:
            match_type = f"starting with '{word}'{' (case insensitive)' if match_mode == 1 else ''}"
        case 2 | 3:
            match_type = f"ending with '{word}'{' (case insensitive)' if match_mode == 3 else ''}"
        case 4 | 5:
            match_type = f"starting or ending with '{word}'{' (case insensitive)' if match_mode == 5 else ''}"
        case 6:
            match_type = "with uppercase letters only"
        case 7:
            match_type = "with lowercase letters only"
        case 8:
            match_type = "with digits only"
        case 9:
            match_type = "with uppercase + digits only"
        case 10:
            match_type = "with lowercase + digits only"
        case 11:
            match_type = "with uppercase + lowercase only"
        case 12 | 13:
            match_type = f"starting with {len(word)} repeating characters{' (case insensitive)' if match_mode == 13 else ''}"
        case 14 | 15:
            match_type = f"ending with {len(word)} repeating characters{' (case insensitive)' if match_mode == 15 else ''}"
        case 16 | 17:
            match_type = f"starting or ending with {len(word)} repeating characters{' (case insensitive)' if match_mode == 17 else ''}"

    click.echo(f"Grinding for {limit} keys {match_type}")


def write_key(privkey, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    priv_bytes = privkey[0:64].tobytes()
    pub_bytes = privkey[32:64].tobytes()

    pub_b58 = str(b58encode(pub_bytes), "utf-8")
    priv_b58 = str(b58encode(priv_bytes), "utf-8")
    click.echo(f"Found {pub_b58}")

    json_file_path = Path(output_dir) / f"key_{pub_b58}.json"
    json_file_path.write_text(json.dumps(list(privkey.tobytes())))

    txt_file_path = Path(output_dir) / f"key_{pub_b58}.txt"
    txt_file_path.write_text(priv_b58)


def validate_arguments(mode, word, length, limit, output_dir, global_work_size, local_work_size):
    # validate mode
    if mode is None or mode < 0 or mode > 17:
        click.echo("Invalid --mode", err=True)
        help([])
        exit(1)

    # validate word
    if mode in [0, 1, 2, 3, 4, 5] and (word is None or len(word) == 0):
        click.echo("Empty --word for prefix/suffix match mode", err=True)
        exit(1)

    # validate word characters
    if mode in [0, 1, 2, 3, 4, 5]:
        for c in word:
            alphabet_str = alphabet.decode("utf-8")
            char = c.lower() if mode in [1, 3, 5] else c
            charset = alphabet_str.lower() if mode in [1, 3, 5] else alphabet_str
            if char not in charset:
                click.echo(f"Invalid character in --word: {c}", err=True)
                exit(1)

    # validate length
    if mode in [12, 13, 14, 15, 16, 17]:
        if length is None or length < 0:
            click.echo("Word --length too short for repeating prefix/suffix match mode", err=True)
            exit(1)

    # validate global work size
    if global_work_size < 0 or global_work_size & (global_work_size - 1) != 0:
        click.echo("Invalid --global-work-size, must be a power of 2", err=True)
        exit(1)

    # validate local work size
    if local_work_size < 0 or local_work_size & (local_work_size - 1) != 0 or local_work_size > global_work_size:
        click.echo("Invalid --local-work-size, must be a power of 2, and less than --global-work-size", err=True)
        exit(1)


def generate_vanity_addresses(match_mode=0, word="", limit=1, output_dir="./keys", global_work_size=65536, local_work_size=256):
    device = select_device()
    ctx, queue = initiate_context(device)

    word_bytes = np.frombuffer(word.encode("ascii"), dtype=np.uint8)
    word_len = np.uint32(len(word))

    # Start with random base seed
    base_seed = os.urandom(32)

    base_seed_buf = np.frombuffer(base_seed, dtype=np.uint8)
    count_buf = np.zeros(1, dtype=np.uint32)

    # Allocate GPU memory and copy input data immediately
    base_seed_mem = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=base_seed_buf)
    results_mem = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, RESULT_SIZE)
    count_mem = cl.Buffer(ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=count_buf)
    word_mem = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=word_bytes)

    # Read kernel source from file
    with open("cl/kernel.cl", "r") as f:
        kernel_source = f.read()

    # Compile kernel for the selected device
    click.echo("Compiling kernel...")
    program = cl.Program(ctx, kernel_source).build(options=["-I", "cl", "-Werror", "-cl-std=cl2.0"])
    click.echo("Done compiling kernel")

    kernel = program.generate_vanity_addresses
    kernel.set_arg(0, base_seed_mem)
    kernel.set_arg(1, results_mem)
    kernel.set_arg(2, count_mem)
    kernel.set_arg(3, np.uint32(match_mode))
    kernel.set_arg(4, word_mem)
    kernel.set_arg(5, word_len)

    print_message(match_mode, word, limit)
    click.echo(f"  >> Launching {global_work_size:,} work-items with {local_work_size:,} threads per work-item...")
    click.echo()

    start_time = time.time()
    last_log_time = int(time.time())
    last_speed_delta = time.time()
    last_attempts_delta = 0
    attemps = 0
    found_keys = 0

    while True:
        # Reset count
        cl.enqueue_copy(queue, count_mem, np.zeros(1, dtype=np.uint32))

        # Launch configurable work-items
        cl.enqueue_nd_range_kernel(queue, kernel, (global_work_size,), (local_work_size,))
        queue.finish()

        # Read ONLY the count
        cl.enqueue_copy(queue, count_buf, count_mem)
        match_count = min(int(count_buf[0]), MAX_MATCHES)  # limit to MAX_MATCHES

        attemps += global_work_size

        if int(time.time()) > last_log_time:
            last_log_time = int(time.time())
            elapsed = time.time() - start_time
            speed = (attemps - last_attempts_delta) / (time.time() - last_speed_delta)
            print(f"Attempts: {attemps:,} | {found_keys} found | {format_rate(speed)} | Time: {format_elapsed(elapsed)}")

        if time.time() - last_speed_delta >= 5:
            last_speed_delta = time.time()
            last_attempts_delta = attemps

        if match_count > 0:
            # Read ONLY the matches (count * 64 bytes)
            actual_results = np.zeros(match_count * 64, dtype=np.uint8)
            cl.enqueue_copy(queue, actual_results, results_mem)

            for i in range(match_count):
                found_keys += 1

                start, end = i * 64, (i + 1) * 64
                privkey = actual_results[start:end]
                write_key(privkey, output_dir)

            if found_keys >= limit:
                click.echo(f"Found {found_keys} keys, exiting...")
                return

        # randomize base seed for the next iteration
        base_seed = os.urandom(32)

        # update GPU buffer
        cl.enqueue_copy(queue, base_seed_mem, np.frombuffer(base_seed, dtype=np.uint8))


@click.group()
def main():
    pass


@main.command(context_settings=dict(show_default=True, terminal_width=120))
@click.option("--mode", "-m", type=click.INT, help="Key matching method (run python main.py help for more info)")
@click.option("--word", "-w", type=click.STRING, help="Prefix/Suffix to match")
@click.option("--length", "-l", type=click.INT, help="Number of repeating characters to match")
@click.option("--limit", "-L", default=1, help="Number of matching keys to find")
@click.option("--output-dir", "-O", default="./keys", help="Output directory")
@click.option("--global-work-size", "-gs", default=1024 * 64, help="Number of work-items to launch")
@click.option("--local-work-size", "-ls", default=32, help="Number of threads per work-item")
def grind(mode, word, length, limit, output_dir, global_work_size, local_work_size):
    """Grind for vanity keypairs"""

    validate_arguments(mode, word, length, limit, output_dir, global_work_size, local_work_size)

    if mode in [6, 7, 8, 9, 10, 11]:
        # make a dummy word for these modes
        word = "a"

    # validate length
    if mode in [12, 13, 14, 15, 16, 17]:
        # make a dummy word with the specified length
        word = "a" * length

    generate_vanity_addresses(
        match_mode=mode,
        word=word,
        limit=limit,
        output_dir=output_dir,
        global_work_size=global_work_size,
        local_work_size=local_work_size,
    )


@main.command()
def help():
    """Print help message for the command arguments"""

    click.echo("Usage: main.py grind [OPTIONS]")
    click.echo()
    click.echo("Options:")
    click.echo("  -m,  --mode             INTEGER  Key matching method")
    click.echo("  -w,  --word             TEXT     Prefix/Suffix to match")
    click.echo("  -l,  --length           INTEGER  Number of repeating characters to match")
    click.echo("  -L,  --limit            INTEGER  Number of matching keys to find  [default: 1]")
    click.echo("  -O,  --output-dir       TEXT     Output directory  [default: ./keys]")
    click.echo("  -gs, --global-work-size INTEGER  Number of work-items to launch  [default: 65536]")
    click.echo("  -ls, --local-work-size  INTEGER  Number of threads per work-item  [default: 32]")
    click.echo()
    click.echo("Modes:")
    click.echo("   0 = match prefix")
    click.echo("   1 = match prefix (case insensitive)")
    click.echo("   2 = match suffix")
    click.echo("   3 = match suffix (case insensitive)")
    click.echo("   4 = match any (prefix or suffix)")
    click.echo("   5 = match any (case insensitive)")
    click.echo("   6 = match only uppercase")
    click.echo("   7 = match only lowercase")
    click.echo("   8 = match only digits")
    click.echo("   9 = match uppercase + digits")
    click.echo("  10 = match lowercase + digits")
    click.echo("  11 = match uppercase + lowercase")
    click.echo("  12 = match repeating prefix")
    click.echo("  13 = match repeating prefix (case insensitive)")
    click.echo("  14 = match repeating suffix")
    click.echo("  15 = match repeating suffix (case insensitive)")
    click.echo("  16 = match repeating any (prefix or suffix)")
    click.echo("  17 = match repeating any (case insensitive)")


if __name__ == "__main__":
    # hijack --help and show the custom help
    if "--help" in sys.argv:
        help([])
        exit(0)

    main()
