"""
Ce script génère des tirages aléatoires pour l'EuroMillions en utilisant des sources d'entropie variées.
"""

import os
import time
import hashlib
import secrets
import random
import socket
import platform
import psutil
import uuid
import threading
import datetime
import multiprocessing
from progress.bar import Bar
import openmeteo_requests
import requests_cache
import numpy as _
from retry_requests import retry
from constants import *

def _fetch_weather_api(params):
    """Internal function to make Open-Meteo API requests"""
    cache_session = requests_cache.CachedSession('.cache', expire_after=60)
    retry_session = retry(cache_session, retries=2, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    return openmeteo.weather_api(OPENMETEO_API_URL, params=params)

def _get_weather_data():
    """Fonction interne qui récupère les données météo de l'API"""
    params = {
        "latitude": random.uniform(-70, 70),
        "longitude": random.uniform(-180, 180),
        "hourly": random.sample(OPENMETEO_HOURLY_PARAMS, random.randint(3, 6)),
        "timezone": "auto"
    }

    responses = _fetch_weather_api(params)
    entropy_values = []
    for i in range(len(params["hourly"])):
        var_values = responses[0].Hourly().Variables(i).ValuesAsNumpy()
        entropy_values.extend(var_values.tolist())

    weather_str = "".join([str(v) for v in entropy_values])
    return hashlib.sha256(weather_str.encode()).hexdigest()

def get_weather_entropy():
    """Récupère des données météo comme source supplémentaire d'entropie"""
    try:
        return _get_weather_data()
    except Exception as e:
        print(f"Erreur lors de la récupération des données météo: {e}")
        fallback = f"weather_fallback_{time.time()}_{random.getrandbits(64)}"
        return hashlib.sha256(fallback.encode()).hexdigest()

def get_static_entropy_pool():
    """Crée un pool d'entropie de base avec des sources qui ne changent pas rapidement"""
    weather_entropy = get_weather_entropy()
    return [
        str(os.urandom(32)),
        str(secrets.token_bytes(32)),
        socket.gethostname(),
        str(platform.system_alias(platform.system(), platform.release(), platform.version())),
        str(uuid.getnode()),
        str(multiprocessing.cpu_count()),
        "".join([str(v) for v in psutil.disk_partitions()]),
        str(hash(frozenset(os.environ.items()))),
        weather_entropy,
    ]

def get_dynamic_entropy_pool():
    """Récupère des données dynamiques pour ajouter de l'entropie"""
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
        str(psutil.net_io_counters().bytes_sent if hasattr(psutil, 'net_io_counters') else 0),
        str(id({})),
    ]

def generate_seed(base_pool=None):
    """Génère une graine aléatoire en combinant différentes sources d'entropie"""
    entropy_sources = base_pool.copy() if base_pool else []
    entropy_sources.extend(get_dynamic_entropy_pool())
    random.shuffle(entropy_sources)

    entropy_str = "".join(entropy_sources)
    intermediate_hash = hashlib.sha512(entropy_str.encode()).digest()
    intermediate_hash = hashlib.blake2b(intermediate_hash).digest()

    final_hash = hashlib.sha256(intermediate_hash).hexdigest()
    return int(final_hash, 16)

def faire_tirage(base_pool=None):
    """Génère un tirage avec N numéros et M étoiles en utilisant une graine aléatoire"""
    seed = generate_seed(base_pool)
    random.seed(seed)
    numeros = random.sample(range(1, MAX_NUMERO + 1), NOMBRE_NUMEROS)
    etoiles = random.sample(range(1, MAX_ETOILE + 1), NOMBRE_ETOILES)
    return {
        "graine": seed,
        "numeros": sorted(numeros),
        "etoiles": sorted(etoiles)
    }

def generate_draws(num_tirages):
    """Génère plusieurs tirages séquentiellement"""
    base_pool = get_static_entropy_pool()
    bar = Bar('Progression', max=num_tirages, suffix='%(percent)d%%')

    tirages = []
    for _ in range(num_tirages):
        tirages.append(faire_tirage(base_pool))
        time.sleep(0.01)
        bar.next()

    bar.finish()
    return tirages

def afficher_tirage(tirage, indice=None, titre="TIRAGE"):
    """Affiche un tirage de façon formatée"""
    print(f"\n===== {titre} =====")
    if indice is not None:
        print(f"Tirage #{indice + 1}")
    print(f"Numéros : {tirage['numeros']}")
    print(f"Étoiles : {tirage['etoiles']}")
    print(f"Graine utilisée : {tirage['graine']}")

def afficher_tirages_supplementaires(tirages, tirages_affiches):
    """Affiche des tirages aléatoires supplémentaires à la demande de l'utilisateur."""
    while len(tirages_affiches) < len(tirages):
        afficher_autre = input("\nVoulez-vous voir un autre tirage aléatoire? (o/n): ").lower().strip()
        if afficher_autre not in ['o', 'oui', 'y', 'yes', '']:
            break

        indices_disponibles = [i for i in range(len(tirages)) if i not in tirages_affiches]
        if not indices_disponibles:
            print("Tous les tirages ont déjà été affichés!")
            break

        indice_nouveau = random.choice(indices_disponibles)
        nouveau_tirage = tirages[indice_nouveau]
        tirages_affiches.add(indice_nouveau)

        afficher_tirage(nouveau_tirage, indice_nouveau, "AUTRE TIRAGE ALÉATOIRE")

if __name__ == "__main__":
    print(f"Génération de {NOMBRE_TIRAGE} tirages différents...")
    tirages = generate_draws(NOMBRE_TIRAGE)

    base_pool = get_static_entropy_pool()
    random.seed(generate_seed(base_pool))
    tirage_choisi = random.choice(tirages)
    tirages_affiches = {tirages.index(tirage_choisi)}

    afficher_tirage(tirage_choisi, titre="RÉSULTAT FINAL")
    print("Tirage sélectionné parmi les", NOMBRE_TIRAGE, "générés")
    afficher_tirages_supplementaires(tirages, tirages_affiches)
