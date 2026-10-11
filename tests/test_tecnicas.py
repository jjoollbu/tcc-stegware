"""Testes automáticos das duas técnicas (ida e volta, alteração mínima, capacidade). Tarefa T1.8 (Osmar e Luiz)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "src"))
import numpy as np, pytest, jpeglib, hashlib
from lsb import esconder_lsb, extrair_lsb
from dct import esconder_dct, extrair_dct, coeficientes_banda, BANDA
from skimage import data

TAMANHOS = [131, 983, 1966]
rng = np.random.default_rng(0)


@pytest.fixture(scope="module")
def capa():
    return data.camera()          # pode trocar por uma capa da BOSSBase


@pytest.fixture(scope="module")
def Y(capa, tmp_path_factory):
    f = tmp_path_factory.mktemp("j") / "c.jpg"
    jpeglib.from_spatial(capa[..., None]).write_spatial(str(f), qt=95)
    return jpeglib.read_dct(str(f)).Y


@pytest.mark.parametrize("n", TAMANHOS)
def test_ida_e_volta_lsb(capa, n):
    pl = rng.integers(0, 256, n, dtype=np.uint8).tobytes()
    assert hashlib.sha256(extrair_lsb(esconder_lsb(capa, pl), n)).digest() == hashlib.sha256(pl).digest()


@pytest.mark.parametrize("n", TAMANHOS)
def test_alteracao_minima_lsb(capa, n):
    pl = rng.integers(0, 256, n, dtype=np.uint8).tobytes()
    d = esconder_lsb(capa, pl).astype(int).ravel() - capa.astype(int).ravel()
    assert np.abs(d).max() <= 1 and not d[n * 8:].any()


@pytest.mark.parametrize("n", TAMANHOS)
def test_ida_e_volta_dct(Y, n):
    pl = rng.integers(0, 256, n, dtype=np.uint8).tobytes()
    assert extrair_dct(esconder_dct(Y, pl), n) == pl


@pytest.mark.parametrize("n", TAMANHOS)
def test_alteracao_minima_dct(Y, n):
    pl = rng.integers(0, 256, n, dtype=np.uint8).tobytes()
    S = esconder_dct(Y, pl)
    fora = np.ones((8, 8), bool)
    for i, j in BANDA: fora[i, j] = False
    assert (S.reshape(-1, 8, 8)[:, fora] == Y.reshape(-1, 8, 8)[:, fora]).all()
    d = coeficientes_banda(S).astype(int) - coeficientes_banda(Y).astype(int)
    assert np.abs(d).max() <= 1 and not np.isin(coeficientes_banda(Y)[d != 0], [0, 1]).any()


def test_capacidade(capa, Y):
    with pytest.raises(ValueError): esconder_lsb(capa, bytes(capa.size // 8 + 1))
    with pytest.raises(ValueError): esconder_dct(Y, bytes(10**6))
