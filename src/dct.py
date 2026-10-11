"""Módulo DCT — esconder, extrair e capacidade. Tarefa T1.6 (Osmar). Ver Seção 3.3.2.

Opera nos coeficientes quantizados do canal Y lidos pela jpeglib, sem recomprimir:
    jpg = jpeglib.read_dct(capa); jpg.Y = esconder_dct(jpg.Y, payload); jpg.write_dct(saida)
As funções não tocam o disco, para o cronômetro medir só o algoritmo (Seção 3.2.3).
"""
import numpy as np

# 26 posições de média frequência (i + j de 4 a 7), em ordem zigue-zague
BANDA = sorted(
    [(i, j) for i in range(8) for j in range(8) if 4 <= i + j <= 7],
    key=lambda p: (p[0] + p[1], p[0] if (p[0] + p[1]) % 2 else -p[0]),
)
_LIN = np.array([p[0] for p in BANDA]); _COL = np.array([p[1] for p in BANDA])


def coeficientes_banda(Y: np.ndarray) -> np.ndarray:
    """Y = coeficientes do JPEG, formato (blocos_v, blocos_h, 8, 8).
    Devolve vetor 1D: blocos em ordem de varredura, 26 posições por bloco."""
    blocos = Y.reshape(-1, 8, 8)
    return blocos[:, _LIN, _COL].ravel()


def posicoes_elegiveis(v: np.ndarray) -> np.ndarray:
    """Índices de v que podem receber bit: coeficientes diferentes de 0 e de 1 (regra Jsteg)."""
    return np.flatnonzero((v != 0) & (v != 1))


def capacidade_dct(Y: np.ndarray) -> int:
    return int(posicoes_elegiveis(coeficientes_banda(Y)).size)


def esconder_dct(Y: np.ndarray, payload: bytes) -> np.ndarray:
    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8)).astype(Y.dtype)
    v = coeficientes_banda(Y).copy()
    pos = posicoes_elegiveis(v)
    if bits.size > pos.size:
        raise ValueError(f"payload ({bits.size} bits) maior que a capacidade ({pos.size} bits)")
    p = pos[: bits.size]
    v[p] = (v[p] & ~1) | bits            # troca o último bit (complemento de dois: -2 vira -1)
    saida = Y.reshape(-1, 8, 8).copy()
    saida[:, _LIN, _COL] = v.reshape(-1, len(BANDA))
    return saida.reshape(Y.shape)


def extrair_dct(Y: np.ndarray, n_bytes: int) -> bytes:
    v = coeficientes_banda(Y)
    p = posicoes_elegiveis(v)[: n_bytes * 8]
    return np.packbits((v[p] & 1).astype(np.uint8)).tobytes()
