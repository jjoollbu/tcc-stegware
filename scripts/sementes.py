"""Seed mestra do TCC e fluxos independentes derivados dela (decisão 8)."""
import numpy as np

SEED_MESTRA = 2026
_fluxos = np.random.SeedSequence(SEED_MESTRA).spawn(4)
RNG_PAYLOADS, RNG_SORTEIO, RNG_ORDEM, RNG_BOOTSTRAP = (np.random.default_rng(s) for s in _fluxos)
