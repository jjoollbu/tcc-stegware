"""Qui-quadrado nas capas limpas (falsos positivos). Tarefa T1.13 (Ana).

Roda o detector nas capas PNG e JPEG SEM payload, na mesma ordem de leitura do executar.py.
Uso: python scripts/analisar_limpas.py piloto | python scripts/analisar_limpas.py experimento
"""
import sys, pathlib
import numpy as np, pandas as pd, jpeglib
from PIL import Image
RAIZ = pathlib.Path(__file__).parents[1]; sys.path.insert(0, str(RAIZ / "src"))
from dct import coeficientes_banda, posicoes_elegiveis
from quiquadrado import p_max

uso = sys.argv[1]; LIMIAR = 0.95
man = pd.read_csv(RAIZ / "dataset/manifest.csv", dtype={"id": str})
linhas = []
for r in man[man.uso == uso].itertuples():
    png = np.array(Image.open(RAIZ / f"dataset/capas/png/{r.id}.png")).ravel()
    v = coeficientes_banda(jpeglib.read_dct(str(RAIZ / f"dataset/capas/jpeg/{r.id}.jpg")).Y)
    linhas += [{"id": r.id, "categoria": r.categoria, "formato": "png", "p_max": p_max(png)},
               {"id": r.id, "categoria": r.categoria, "formato": "jpeg", "p_max": p_max(v[posicoes_elegiveis(v)])}]
df = pd.DataFrame(linhas); df["falso_positivo"] = df.p_max >= LIMIAR
(RAIZ / "resultados" / uso).mkdir(parents=True, exist_ok=True)
df.to_csv(RAIZ / "resultados" / uso / "limpas.csv", index=False, lineterminator="\n")
print(df.groupby("formato").falso_positivo.agg(["sum", "count"]))
