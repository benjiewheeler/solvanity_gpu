import os
import time

import numpy as np
import pyopencl as cl
from base58 import b58encode

# Fixed-size buffers (tune based on GPU memory)
MAX_MATCHES = 256
RESULT_SIZE = MAX_MATCHES * 64  # 64 bytes per private key


platform_name = "AMD Accelerated Parallel Processing"
device_name = "gfx1102"  # RX 7600
# device_name = "gfx1036"  # R5 9600X

platforms = cl.get_platforms()

# Pick AMD's OpenCL runtime explicitly
# Pick the discrete GPU, not the iGPU
platform = next(p for p in platforms if platform_name in p.name)
device = next(d for d in platform.get_devices() if device_name in d.name)

# Create an OpenCL context bound to this device
# Command queue = submission queue for GPU work
ctx = cl.Context([device])
queue = cl.CommandQueue(ctx)


def generate_vanity_addresses(prefix, num_work_items=65536, group_size=256):
    prefix_bytes = np.frombuffer(prefix.encode("ascii"), dtype=np.uint8)
    prefix_len = np.uint32(len(prefix))

    # Start with random base seed
    base_seed = os.urandom(32)

    base_seed_buf = np.frombuffer(base_seed, dtype=np.uint8)
    count_buf = np.zeros(1, dtype=np.uint32)

    # Allocate GPU memory and copy input data immediately
    base_seed_mem = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=base_seed_buf)
    results_mem = cl.Buffer(ctx, cl.mem_flags.WRITE_ONLY, RESULT_SIZE)
    count_mem = cl.Buffer(ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=count_buf)
    prefix_mem = cl.Buffer(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=prefix_bytes)

    # Read kernel source from file
    with open("cl/kernel.cl", "r") as f:
        kernel_source = f.read()

    # Compile kernel for the selected device
    program = cl.Program(ctx, kernel_source).build(options=["-I", "cl", "-Werror", "-cl-std=cl2.0"])

    kernel = program.generate_vanity_addresses
    kernel.set_arg(0, base_seed_mem)
    kernel.set_arg(1, results_mem)
    kernel.set_arg(2, count_mem)
    kernel.set_arg(3, prefix_len)
    kernel.set_arg(4, prefix_mem)

    print(f"Launching {num_work_items:,} work-items with {group_size:,} threads per work-item...")

    iteration = 0
    attemps = 0
    start_time = time.time()

    while True:
        # Reset count
        cl.enqueue_copy(queue, count_mem, np.zeros(1, dtype=np.uint32))

        # Launch configurable work-items
        cl.enqueue_nd_range_kernel(queue, kernel, (num_work_items,), (group_size,))
        queue.finish()

        # Read ONLY result_count (4 bytes)
        cl.enqueue_copy(queue, count_buf, count_mem)
        match_count = min(int(count_buf[0]), MAX_MATCHES)

        iteration += 1
        attemps += num_work_items
        elapsed = time.time() - start_time
        khs = (num_work_items * iteration / 1000) / elapsed
        print(f"Iter {iteration:4d}: {match_count:2d} matches | {khs:7.1f} KH/s | Attempts: {attemps:,}")

        if match_count > 0:
            # Read ONLY the matches (count * 64 bytes)
            actual_results = np.zeros(match_count * 64, dtype=np.uint8)
            cl.enqueue_copy(queue, actual_results, results_mem)

            print(f"🎉 Found {match_count} matching private keys for prefix '{prefix}'!")
            for i in range(match_count):
                start, end = i * 64, (i + 1) * 64
                privkey = actual_results[start:end]
                priv_b58 = b58encode(privkey[0:64].tobytes())
                pub_b58 = b58encode(privkey[32:64].tobytes())
                print(f"  #{i+1:2d}: {priv_b58} | {pub_b58}")

            return True

        # Update GPU buffer
        base_seed = os.urandom(32)
        cl.enqueue_copy(queue, base_seed_mem, np.frombuffer(base_seed, dtype=np.uint8))

    return None


# Usage - Ultra-conservative testing
if __name__ == "__main__":
    prefix = "Word"

    generate_vanity_addresses(
        prefix,
        num_work_items=(1024 * 1024),
        group_size=(256),
    )
