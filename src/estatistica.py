"""Funções da análise estatística. Tarefa T1.14 (Ana). Ver Seção 3.6.

Testes pareados LSB × DCT (a mesma imagem passa pelas duas técnicas, decisão D-17), razão de
tempos com IC 95% por bootstrap, McNemar exato na detecção, IC de Wilson para FP/FN e
correção de Benjamini-Hochberg dentro de cada família (decisão D-15).
"""
import numpy as np
from scipy import stats
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.proportion import proportion_confint
from statsmodels.stats.multitest import multipletests


def comparar_pareado(lsb: np.ndarray, dct: np.ndarray) -> dict:
    """lsb[i] e dct[i] = mesma imagem. Escolhe t pareado ou Wilcoxon pela normalidade das diferenças."""
    d = dct - lsb
    normal = stats.shapiro(d).pvalue >= 0.05
    if normal:
        p = stats.ttest_rel(dct, lsb).pvalue
        efeito = d.mean() / d.std(ddof=1)                     # d de Cohen para pares
        teste = "t pareado"
    else:
        p = stats.wilcoxon(dct, lsb).pvalue
        dz = d[d != 0]; n = dz.size
        postos = stats.rankdata(np.abs(dz)); w_mais = postos[dz > 0].sum()
        z = (w_mais - n * (n + 1) / 4) / np.sqrt(n * (n + 1) * (2 * n + 1) / 24)
        efeito = z / np.sqrt(n)                               # r = Z / raiz(n)
        teste = "Wilcoxon"
    return {"teste": teste, "p": p, "efeito": efeito, "n": d.size}


def razao_tempo(t_lsb: np.ndarray, t_dct: np.ndarray, seed: int) -> dict:
    """Razão DCT/LSB (média geométrica) com IC 95% por bootstrap."""
    log_r = np.log(t_dct / t_lsb)
    ic = stats.bootstrap((log_r,), np.mean, n_resamples=10_000, confidence_level=0.95,
                         random_state=np.random.default_rng(seed)).confidence_interval
    return {"razao": np.exp(log_r.mean()), "ic_inf": np.exp(ic.low), "ic_sup": np.exp(ic.high)}


def comparar_deteccao(det_lsb: np.ndarray, det_dct: np.ndarray) -> dict:
    """det_* = vetores booleanos (detectado?) para as mesmas imagens."""
    tabela = [[np.sum(det_lsb & det_dct), np.sum(det_lsb & ~det_dct)],
              [np.sum(~det_lsb & det_dct), np.sum(~det_lsb & ~det_dct)]]
    return {"p": mcnemar(tabela, exact=True).pvalue}


def taxa_com_ic(eventos: int, n: int) -> tuple:
    inf, sup = proportion_confint(eventos, n, alpha=0.05, method="wilson")
    return eventos / n, inf, sup


def corrigir_bh(pvalores: list) -> np.ndarray:
    return multipletests(pvalores, alpha=0.05, method="fdr_bh")[1]
