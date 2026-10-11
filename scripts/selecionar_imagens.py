"""Calcula textura e capacidade DCT de toda a base, define categorias e sorteia as imagens.
Tarefa T1.4 (Luiz)."""
import sys, pathlib, hashlib, tempfile
import numpy as np, pandas as pd, jpeglib
from PIL import Image
from skimage.filters import sobel
sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "src"))
from dct import capacidade_dct
from sementes import RNG_SORTEIO

ORIGEM = pathlib.Path("dataset/bossbase")  # 10.000 arquivos .pgm
MINIMO_BITS = 17_301                       # 110% da taxa alta (15.728 bits)
POR_CATEGORIA, PILOTO = 30, 10

linhas = []
with tempfile.TemporaryDirectory() as tmp:
    for f in sorted(ORIGEM.glob("*.pgm")):
        img = np.array(Image.open(f))
        assert img.shape == (512, 512) and img.dtype == np.uint8, f
        jpeglib.from_spatial(img[..., None]).write_spatial(f"{tmp}/t.jpg", qt=95)
        linhas.append({
            "id": f.stem,
            "gradiente": float(sobel(img / 255.0).mean()),
            "capacidade_dct_bits": capacidade_dct(jpeglib.read_dct(f"{tmp}/t.jpg").Y),
            "sha256_original": hashlib.sha256(f.read_bytes()).hexdigest(),
        })
df = pd.DataFrame(linhas)
df["quintil"] = pd.qcut(df["gradiente"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
df["elegivel"] = df["capacidade_dct_bits"] >= MINIMO_BITS
df.to_csv("dataset/todas_imagens.csv", index=False, lineterminator="\n")  # LF: mesmo SHA-256 no Windows e na VM

sorteio = []
for quintil, categoria in [(1, "baixa"), (3, "media"), (5, "alta")]:
    cand = df[(df.quintil == quintil) & df.elegivel].sort_values("id")
    print(f"quintil {quintil}: {len(cand)} elegíveis de {(df.quintil == quintil).sum()}")
    if len(cand) < POR_CATEGORIA + PILOTO:
        sys.exit(f"Poucas elegíveis no quintil {quintil}: acionar plano B (taxa alta 0,05 bpp)")
    escolhidas = RNG_SORTEIO.choice(cand["id"].to_numpy(), POR_CATEGORIA + PILOTO, replace=False)
    for k, img_id in enumerate(escolhidas):
        sorteio.append({"id": img_id, "categoria": categoria,
                        "uso": "experimento" if k < POR_CATEGORIA else "piloto"})
sel = pd.DataFrame(sorteio).merge(df, on="id")
sel.to_csv("dataset/selecao.csv", index=False, lineterminator="\n")  # LF: mesmo SHA-256 no Windows e na VM
