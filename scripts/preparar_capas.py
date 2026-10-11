"""Gera as capas PNG e JPEG (QF 95) das imagens sorteadas e completa o manifest.
Tarefa T1.5 (Luiz)."""
import hashlib, pathlib
import numpy as np, pandas as pd, jpeglib
from PIL import Image

sel = pd.read_csv("dataset/selecao.csv", dtype={"id": str})
png_dir, jpg_dir = pathlib.Path("dataset/capas/png"), pathlib.Path("dataset/capas/jpeg")
png_dir.mkdir(parents=True, exist_ok=True); jpg_dir.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for i, r in sel.iterrows():
    img = np.array(Image.open(f"dataset/bossbase/{r.id}.pgm"))
    Image.fromarray(img).save(png_dir / f"{r.id}.png", compress_level=6)
    jpeglib.from_spatial(img[..., None]).write_spatial(str(jpg_dir / f"{r.id}.jpg"), qt=95)
    sel.loc[i, "sha256_png"] = sha(png_dir / f"{r.id}.png")
    sel.loc[i, "sha256_jpeg"] = sha(jpg_dir / f"{r.id}.jpg")
sel.insert(1, "fonte", "BOSSBase 1.01")
sel.insert(2, "resolucao", "512x512"); sel.insert(3, "profundidade_bits", 8)
sel.to_csv("dataset/manifest.csv", index=False, lineterminator="\n")  # LF: mesmo SHA-256 no Windows e na VM
print(len(sel), "imagens prontas")
