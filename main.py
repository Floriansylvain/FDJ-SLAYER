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
from concurrent.futures import ProcessPoolExecutor
import openmeteo_requests
import requests_cache
from retry_requests import retry

def fetch_weather_entropy():
    """Récupère des données météo comme source supplémentaire d'entropie"""
    try:
        # Configuration du client API Open-Meteo avec cache et nouvelle tentative en cas d'erreur
        cache_session = requests_cache.CachedSession('.cache', expire_after=60)  # Courte durée de cache
        retry_session = retry(cache_session, retries=2, backoff_factor=0.2)  # Nouvelle tentative rapide
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # Demande de données météo avec un délai d'expiration
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 50.4,
            "longitude": 1.83,
            "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", 
                      "visibility", "precipitation", "cloud_cover"],
            "timezone": "auto"
        }

        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        # Extraction de toutes les valeurs numériques des prévisions horaires
        entropy_values = []
        hourly = response.Hourly()

        # Traitement de chaque variable météorologique
        for i in range(len(params["hourly"])):
            var_values = hourly.Variables(i).ValuesAsNumpy()
            entropy_values.extend(var_values.tolist())

        # Création d'un hash de toutes les données météorologiques
        weather_str = "".join([str(v) for v in entropy_values])
        weather_hash = hashlib.sha256(weather_str.encode()).hexdigest()

        return weather_hash
    except Exception as e:
        # If anything fails, return a timestamp-based fallback
        fallback = f"weather_fallback_{time.time()}_{random.getrandbits(64)}"
        return hashlib.sha256(fallback.encode()).hexdigest()

def initialize_entropy_pool():
    """Crée un pool d'entropie de base avec des sources qui ne changent pas rapidement"""
    weather_entropy = fetch_weather_entropy()

    return [
        str(os.urandom(32)),  # 32 octets d'aléa du système
        str(secrets.token_bytes(32)),  # Autre source cryptographique
        socket.gethostname(),  # Nom de l'hôte
        str(platform.system_alias(platform.system(), platform.release(), platform.version())),
        str(uuid.getnode()),  # Adresse MAC
        str(multiprocessing.cpu_count()),  # Nombre de CPU
        "".join([str(v) for v in psutil.disk_partitions()]),  # Configuration des disques
        str(hash(frozenset(os.environ.items()))),  # Variables d'environnement,
        weather_entropy, # Données météorologiques
    ]

def generate_seed(base_pool=None):
    """Génère une graine aléatoire en combinant différentes sources d'entropie"""
    # Utiliser le pool de base si fourni, sinon créer des sources complètes
    if base_pool:
        entropy_sources = base_pool.copy()
    else:
        entropy_sources = []

    # Ajouter les sources dynamiques qui changent à chaque appel
    dynamic_sources = [
        str(time.time()),  # Timestamp actuel
        hashlib.sha256(str(time.perf_counter()).encode()).hexdigest(),  # Timer haute précision hashé
        str(os.getpid()),  # ID du processus
        str(psutil.cpu_percent(interval=0.01)),  # Utilisation CPU (réduit à 0.01)
        str(psutil.virtual_memory().percent),  # Utilisation mémoire
        str(psutil.disk_usage('/').percent),  # Utilisation disque
        str(random.getrandbits(256)),  # Bits aléatoires du générateur par défaut
        str(datetime.datetime.now().microsecond),  # Microsecondes actuelles
        str(threading.active_count()),  # Nombre de threads actifs
        str(sum(psutil.cpu_times())),  # Temps CPU cumulés
        str(psutil.net_io_counters().bytes_sent if hasattr(psutil, 'net_io_counters') else 0),  # Trafic réseau
        str(id({})),  # Adresse mémoire d'un nouvel objet
    ]

    entropy_sources.extend(dynamic_sources)

    random.shuffle(entropy_sources)

    # Concaténer et hacher plusieurs fois avec différents algorithmes
    entropy_str = "".join(entropy_sources)
    intermediate_hash = hashlib.sha512(entropy_str.encode()).digest()
    intermediate_hash = hashlib.blake2b(intermediate_hash).digest()

    # Utiliser un hachage final pour obtenir un entier
    final_hash = hashlib.sha256(intermediate_hash).hexdigest()
    seed = int(final_hash, 16)

    return seed

def faire_tirage(base_pool=None):
    """Génère un tirage avec 5 numéros et 2 étoiles en utilisant une graine aléatoire"""
    # Génération de nouveaux nombres avec une nouvelle graine
    seed = generate_seed(base_pool)
    random.seed(seed)
    numeros = random.sample(range(1, 51), 5)
    etoiles = random.sample(range(1, 13), 2)
    return {
        "graine": seed,
        "numeros": sorted(numeros),
        "etoiles": sorted(etoiles)
    }

def worker_process(num_tirages, base_pool):
    """Fonction exécutée par chaque processus travailleur"""
    local_tirages = []
    for _ in range(num_tirages):
        local_tirages.append(faire_tirage(base_pool))
    return local_tirages

def generate_draws(num_tirages):
    """Génère plusieurs tirages en parallèle"""
    # Initialiser le pool d'entropie de base
    base_pool = initialize_entropy_pool()

    # Déterminer le nombre optimal de processus
    num_processes = min(os.cpu_count() or 4, 4)  # Limiter à un nombre raisonnable

    # Répartir le travail entre les processus
    tirages_par_processus = num_tirages // num_processes
    remainder = num_tirages % num_processes

    # Préparer les tâches pour chaque processus
    tasks = []
    for i in range(num_processes):
        count = tirages_par_processus + (1 if i < remainder else 0)
        if count > 0:
            tasks.append((count, base_pool))

    bar = Bar('Progression', max=num_tirages, suffix='%(percent)d%%')

    # Exécuter les tâches en parallèle
    tirages = []
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = [executor.submit(worker_process, count, bp) for count, bp in tasks]
        for future in futures:
            batch = future.result()
            tirages.extend(batch)
            bar.next(len(batch))

    bar.finish()
    return tirages

if __name__ == "__main__":
    print("Génération de 100 tirages différents...")
    tirages = generate_draws(100)

    # Mélange final pour le choix du tirage avec une nouvelle graine
    base_pool = initialize_entropy_pool()
    random.seed(generate_seed(base_pool))
    tirage_choisi = random.choice(tirages)

    print("\n===== RÉSULTAT FINAL =====")
    print("Tirage sélectionné parmi les 100 générés")
    print("Graine utilisée :", tirage_choisi["graine"])
    print("Numéros :", tirage_choisi["numeros"])
    print("Étoiles :", tirage_choisi["etoiles"])

    # Demander à l'utilisateur s'il souhaite afficher tous les tirages
    afficher_tous = input("\nVoulez-vous afficher tous les tirages générés? (o/n): ").lower().strip()
    if afficher_tous in ['o', 'oui', 'y', 'yes']:
        print("\n===== TOUS LES TIRAGES =====")
        for i, tirage in enumerate(tirages, 1):
            print(f"Tirage {i}:")
            print(f"  Numéros: {tirage['numeros']}")
            print(f"  Étoiles: {tirage['etoiles']}")
            print(f"  Graine: {tirage['graine']}")
            print("-" * 30)

    input("\nAppuyez sur Entrée pour quitter...")