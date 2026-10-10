import numpy as np
import jpeglib
import hashlib
import os
import cv2
import matplotlib.pyplot as plt

def get_zigzag_band():
    """
    Retorna as coordenadas (i, j) em ordem de zigue-zague para o bloco 8x8.
    Filtra apenas a banda de média frequência onde 4 <= i + j <= 7 (26 posições),
    conforme exigido na Seção 3.3.2.
    """
    zigzag = []
    for d in range(15):
        if d % 2 == 0:
            for i in range(d, -1, -1):
                j = d - i
                if i < 8 and j < 8:
                    zigzag.append((i, j))
        else:
            for i in range(d + 1):
                j = d - i
                if i < 8 and j < 8:
                    zigzag.append((i, j))
    return [(i, j) for (i, j) in zigzag if 4 <= i + j <= 7]

# Banda de frequências médias (26 posições constantes)
BAND = get_zigzag_band()

def encode_dct(image_path, payload_bytes, output_path):
    """
    Esconde bytes em um arquivo JPEG através de inserção direta nos coeficientes
    quantizados da banda de média frequência (4 <= i+j <= 7).
    Usa LSB Replacement apenas em coeficientes != 0 e != 1 (Regra Jsteg).
    Não adiciona nenhum cabeçalho de tamanho (inércia do payload).
    """
    # Lê a estrutura completa do JPEG sem recomprimir
    im = jpeglib.read_dct(image_path)
    Y = im.Y # Matriz de luminância (blocos_Y, blocos_X, 8, 8)
    
    # Prepara a carga (payload) em bits
    binary_message = "".join([f"{b:08b}" for b in payload_bytes])
    bit_len = len(binary_message)
    
    # 1. Validação de capacidade
    capacity = 0
    for block_y in range(Y.shape[0]):
        for block_x in range(Y.shape[1]):
            for (i, j) in BAND:
                c = int(Y[block_y, block_x, i, j])
                if c != 0 and c != 1:
                    capacity += 1
                    
    if bit_len > capacity:
        raise ValueError(
            f"Erro: Capacidade excedida. "
            f"A imagem suporta {capacity} bits ({capacity//8} bytes), "
            f"mas o payload tem {bit_len} bits ({bit_len//8} bytes)."
        )
        
    # 2. Inserção (da esquerda para direita, cima para baixo)
    bit_idx = 0
    for block_y in range(Y.shape[0]):
        for block_x in range(Y.shape[1]):
            for (i, j) in BAND:
                if bit_idx >= bit_len:
                    break
                
                c = int(Y[block_y, block_x, i, j])
                if c != 0 and c != 1:
                    bit = int(binary_message[bit_idx])
                    # Substitui o último bit mantendo o sinal int16 intacto (inclusive negativos)
                    Y[block_y, block_x, i, j] = (c & ~1) | bit
                    bit_idx += 1
                    
            if bit_idx >= bit_len:
                break
        if bit_idx >= bit_len:
            break
            
    # Salva o arquivo sobrescrevendo os coeficientes sem alterar a quantização original
    im.write_dct(output_path)
    return capacity

def decode_dct(image_path, payload_size_bytes):
    """
    Lê o JPEG e extrai a quantidade exata de bytes informada pelo parâmetro.
    Segue a mesma ordem (esquerda-direita, cima-baixo, zigue-zague).
    """
    im = jpeglib.read_dct(image_path)
    Y = im.Y
    
    bit_len = payload_size_bytes * 8
    extracted_bits = []
    
    for block_y in range(Y.shape[0]):
        for block_x in range(Y.shape[1]):
            for (i, j) in BAND:
                if len(extracted_bits) >= bit_len:
                    break
                c = int(Y[block_y, block_x, i, j])
                if c != 0 and c != 1:
                    # Extrai o bit menos significativo
                    extracted_bits.append(str(c & 1))
                    
            if len(extracted_bits) >= bit_len:
                break
        if len(extracted_bits) >= bit_len:
            break
            
    bits_str = "".join(extracted_bits)
    bytes_arr = bytearray()
    for k in range(0, len(bits_str), 8):
        bytes_arr.append(int(bits_str[k:k+8], 2))
        
    return bytes_arr

def compare_histograms(img1_path, img2_path, output_path="histograma_dct.png"):
    """
    Gera um histograma comparando a imagem original com a estego. (Etapa 3 de automação)
    """
    img1 = cv2.imread(img1_path, cv2.IMREAD_COLOR)
    img2 = cv2.imread(img2_path, cv2.IMREAD_COLOR)

    if img1 is None or img2 is None:
        print("Erro: Imagem(ns) não encontrada(s) para o histograma.")
        return

    plt.figure(figsize=(10, 5))
    colors = ('b', 'g', 'r')
    
    plt.subplot(1, 2, 1)
    plt.title('Histograma - Capa (Original)')
    for idx, col in enumerate(colors):
        hist = cv2.calcHist([img1], [idx], None, [256], [0, 256])
        plt.plot(hist, color=col, alpha=0.7)
        plt.xlim([0, 256])

    plt.subplot(1, 2, 2)
    plt.title('Histograma - Estego (Modificada)')
    for idx, col in enumerate(colors):
        hist = cv2.calcHist([img2], [idx], None, [256], [0, 256])
        plt.plot(hist, color=col, alpha=0.7)
        plt.xlim([0, 256])

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

# ---------------------------------------------------------
# Testes Automáticos Pytest (Conforme Seção 3.3.3 do TCC)
# ---------------------------------------------------------

def setup_test_image():
    # Cria uma imagem de teste temporária em JPEG para uso nos testes
    if not os.path.exists("test_capa.jpeg"):
        img = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
        cv2.imwrite("test_capa.jpeg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

def test_ida_e_volta():
    """ 1. O payload extraído tem o mesmo SHA-256 do original """
    setup_test_image()
    payload = os.urandom(131) # Payload de baixa taxa (131 bytes)
    hash_original = hashlib.sha256(payload).hexdigest()
    
    encode_dct("test_capa.jpeg", payload, "test_estego.jpeg")
    
    payload_extraido = decode_dct("test_estego.jpeg", len(payload))
    hash_extraido = hashlib.sha256(payload_extraido).hexdigest()
    
    assert hash_original == hash_extraido, "Falha: O hash do arquivo extraído é diferente!"

def test_alteracao_minima():
    """ 2. Só coeficientes elegíveis da banda podem mudar """
    setup_test_image()
    payload = os.urandom(50)
    encode_dct("test_capa.jpeg", payload, "test_estego.jpeg")
    
    im_capa = jpeglib.read_dct("test_capa.jpeg")
    im_estego = jpeglib.read_dct("test_estego.jpeg")
    
    diff = im_capa.Y != im_estego.Y
    blocos_diferentes = np.where(diff)
    
    # Verifica cada coeficiente modificado
    for b_y, b_x, i, j in zip(*blocos_diferentes):
        # A posição deve estar na banda de media frequência
        assert (i, j) in BAND, f"Coeficiente modificado fora da banda: ({i}, {j})"
        
        # O valor original não pode ser 0 nem 1
        orig_val = im_capa.Y[b_y, b_x, i, j]
        assert orig_val not in (0, 1), f"Coeficiente {orig_val} modificado indevidamente!"

def test_protecao_capacidade():
    """ 3. Payload maior que a capacidade gera erro em vez de cortar em silêncio """
    setup_test_image()
    # Tenta embutir 50.000 bytes em uma imagem de 256x256 que claramente não suporta
    payload_gigante = os.urandom(50000)
    
    try:
        encode_dct("test_capa.jpeg", payload_gigante, "test_estego.jpeg")
        assert False, "O código deveria ter gerado ValueError por falta de capacidade."
    except ValueError:
        pass # Comportamento correto!

if __name__ == "__main__":
    print("Executando módulo principal...")
    setup_test_image()
    
    # Simulando um payload do TCC (ex: 131 bytes)
    payload_teste = b"Este e um teste simulando o payload inerte. " * 3
    print(f"Payload gerado ({len(payload_teste)} bytes).")
    
    encode_dct("test_capa.jpeg", payload_teste, "test_estego.jpeg")
    print("Ocultação concluída (secreta salva em test_estego.jpeg).")
    
    payload_recuperado = decode_dct("test_estego.jpeg", len(payload_teste))
    print(f"Recuperação concluída: {payload_recuperado[:30]}...")
    
    # Roda a terceira etapa de automatização
    compare_histograms("test_capa.jpeg", "test_estego.jpeg")
    print("Histograma gerado em 'histograma_dct.png'.")
