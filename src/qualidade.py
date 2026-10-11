"""Métricas de qualidade (MSE, PSNR, SSIM). Tarefa T1.9 (Ana). Ver Seção 3.5.2.

SSIM nos parâmetros de Wang et al. (2004): janela gaussiana com sigma 1,5 e covariância
populacional. Recebe os pixels já decodificados (uint8, tons de cinza):
    LSB: capa PNG × estego PNG
    DCT: capa JPEG × estego JPEG, ambas decodificadas (decisão D-19; o executar.py faz isso)
"""
import numpy as np
from skimage.metrics import mean_squared_error, peak_signal_noise_ratio, structural_similarity


def qualidade(capa: np.ndarray, estego: np.ndarray) -> dict:
    a, b = capa.astype(np.float64), estego.astype(np.float64)
    return {
        "mse": mean_squared_error(a, b),
        "psnr": peak_signal_noise_ratio(a, b, data_range=255),
        "ssim": structural_similarity(a, b, data_range=255, gaussian_weights=True,
                                      sigma=1.5, use_sample_covariance=False),
    }
