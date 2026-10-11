"""Gera os três artefatos simulados e inertes (bytes pseudoaleatórios) — decisão 8 / T1.2."""
import hashlib, pathlib
from sementes import RNG_PAYLOADS

TAMANHOS = {"baixa": 131, "media": 983, "alta": 1966}  # 0,004 · 0,03 · 0,06 bpp em 512×512

pasta = pathlib.Path("dataset/payloads")
pasta.mkdir(parents=True, exist_ok=True)

for nome, n in TAMANHOS.items():  # ordem fixa: baixa, media, alta
    dados = RNG_PAYLOADS.integers(0, 256, n, dtype="uint8").tobytes()
    (pasta / f"payload_{nome}.bin").write_bytes(dados)
    print(nome, n, hashlib.sha256(dados).hexdigest())
