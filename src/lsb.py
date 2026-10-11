"""Módulo LSB — esconder e extrair. Tarefa T1.7 (Luiz). Ver Seção 3.3.1.

Recebe e devolve o array de pixels em tons de cinza (uint8), sem tocar o disco, para o
cronômetro medir só o algoritmo (Seção 3.2.3). A estego é gravada sempre em PNG com Pillow:
    Image.fromarray(esconder_lsb(capa, payload)).save(saida_png, compress_level=6)
"""
import numpy as np


def esconder_lsb(capa: np.ndarray, payload: bytes) -> np.ndarray:
    """Grava os bits do payload no último bit dos pixels, em ordem de varredura."""
    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
    plano = capa.ravel()
    if bits.size > plano.size:
        raise ValueError(f"payload ({bits.size} bits) maior que a capacidade ({plano.size} bits)")
    estego = plano.copy()
    estego[:bits.size] = (estego[:bits.size] & 0xFE) | bits
    return estego.reshape(capa.shape)


def extrair_lsb(estego: np.ndarray, n_bytes: int) -> bytes:
    bits = estego.ravel()[: n_bytes * 8] & 1
    return np.packbits(bits).tobytes()
