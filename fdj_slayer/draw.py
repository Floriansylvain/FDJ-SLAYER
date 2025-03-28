"""
This module handles the generation and display of lottery draws.
"""

import os
import time
import hashlib
import secrets
import random
import socket
import platform
import uuid
import threading
import datetime
import multiprocessing
import psutil
from progress.bar import Bar

from .constants import MAX_NUMBER, MAX_STAR, NUMBER_OF_NUMBERS, NUMBER_OF_STARS


class Draw:
    """Handles the generation and display of lottery draws"""

    def __init__(self, weather_service):
        self.weather_service = weather_service

    def get_static_entropy_pool(self):
        """Creates a base entropy pool with sources that don't change rapidly"""
        weather_entropy = self.weather_service.get_weather_entropy()
        return [
            str(os.urandom(32)),
            str(secrets.token_bytes(32)),
            socket.gethostname(),
            str(platform.system_alias(platform.system(),
                platform.release(), platform.version())),
            str(uuid.getnode()),
            str(multiprocessing.cpu_count()),
            "".join([str(v) for v in psutil.disk_partitions()]),
            str(hash(frozenset(os.environ.items()))),
            weather_entropy,
        ]

    def get_dynamic_entropy_pool(self):
        """Retrieves dynamic data to add entropy"""
        return [
            str(time.time()),
            hashlib.sha256(str(time.perf_counter()).encode()).hexdigest(),
            str(os.getpid()),
            str(psutil.cpu_percent(interval=0.01)),
            str(psutil.virtual_memory().percent),
            str(psutil.disk_usage('/').percent),
            str(random.getrandbits(256)),
            str(datetime.datetime.now().microsecond),
            str(threading.active_count()),
            str(sum(psutil.cpu_times())),
            str(psutil.net_io_counters().bytes_sent if hasattr(
                psutil, 'net_io_counters') else 0),
            str(id({})),
        ]

    def generate_seed(self, base_pool=None):
        """Generates a random seed by combining different entropy sources"""
        entropy_sources = base_pool.copy() if base_pool else []
        entropy_sources.extend(self.get_dynamic_entropy_pool())
        random.shuffle(entropy_sources)

        entropy_str = "".join(entropy_sources)
        intermediate_hash = hashlib.sha512(entropy_str.encode()).digest()
        intermediate_hash = hashlib.blake2b(intermediate_hash).digest()

        final_hash = hashlib.sha256(intermediate_hash).hexdigest()
        return int(final_hash, 16)

    def make_draw(self, base_pool=None):
        """Generates a draw with N numbers and M stars using a random seed"""
        seed = self.generate_seed(base_pool)
        random.seed(seed)
        numbers = random.sample(range(1, MAX_NUMBER + 1), NUMBER_OF_NUMBERS)
        stars = random.sample(range(1, MAX_STAR + 1), NUMBER_OF_STARS)
        return {
            "seed": seed,
            "numbers": sorted(numbers),
            "stars": sorted(stars)
        }

    def generate_draws(self, num_draws):
        """Generates multiple draws sequentially"""
        base_pool = self.get_static_entropy_pool()
        progress_bar = Bar('Progress', max=num_draws, suffix='%(percent)d%%')

        draws = []
        for _ in range(num_draws):
            draws.append(self.make_draw(base_pool))
            time.sleep(0.01)
            progress_bar.next()

        progress_bar.finish()
        return draws

    def display_draw(self, draw, index=None, title="DRAW"):
        """Displays a draw in a formatted way"""
        print(f"\n===== {title} =====")
        if index is not None:
            print(f"Draw #{index + 1}")
        print(f"Numbers: {draw['numbers']}")
        print(f"Stars: {draw['stars']}")
        print(f"Seed used: {draw['seed']}")

    def display_additional_draws(self, draws, displayed_draws):
        """Displays additional random draws at the user's request."""
        while len(displayed_draws) < len(draws):
            display_another = input(
                "\nDo you want to see another random draw? (y/n): ").lower().strip()
            if display_another not in ['o', 'oui', 'y', 'yes', '']:
                break

            available_indices = [i for i in range(
                len(draws)) if i not in displayed_draws]
            if not available_indices:
                print("All draws have already been displayed!")
                break

            new_index = random.choice(available_indices)
            new_draw = draws[new_index]
            displayed_draws.add(new_index)

            self.display_draw(new_draw, new_index, "ANOTHER RANDOM DRAW")
