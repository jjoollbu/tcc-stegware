import cv2
import numpy as np
import hashlib
import os
import matplotlib.pyplot as plt

def encode_lsb(image_path, payload_bytes, output_path):
    """
    Oculta bytes em uma imagem usando substituição do bit menos significativo (LSB).
    Conforme Seção 3.3.1: 
    - Sequencial (do canto superior esquerdo, linha a linha).
    - 1 bit por pixel.
    - Por substituição (replacement).
    - Não adiciona delimitador.
    """
    # Lê a imagem em escala de cinza (BOSSBase usa tons de cinza)
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    # Converte o payload de bytes para uma string de bits
    binary_message = ''.join([f'{b:08b}' for b in payload_bytes])
    bit_len = len(binary_message)
    
    # A capacidade em bits é igual ao número total de pixels na imagem em escala de cinza
    total_pixels = image.size
    if bit_len > total_pixels:
        raise ValueError(
            f"Erro: Capacidade excedida. "
            f"A imagem suporta {total_pixels} bits ({total_pixels//8} bytes), "
            f"mas o payload tem {bit_len} bits ({bit_len//8} bytes)."
        )

    # Achata a imagem para processamento sequencial
    flat_image = image.flatten()

    # Substituição (replacement): zera o último bit e soma o novo bit
    for i in range(bit_len):
        flat_image[i] = (flat_image[i] & 254) | int(binary_message[i])

    # Remonta a imagem para suas dimensões originais
    encoded_image = flat_image.reshape(image.shape)
    
    # Salva a imagem estego (obrigatoriamente PNG para não perder os bits via compressão)
    cv2.imwrite(output_path, encoded_image)
    return total_pixels

def decode_lsb(image_path, payload_size_bytes):
    """
    Extrai bytes ocultos via LSB, sabendo previamente o tamanho do payload.
    Lê os primeiros n pixels e extrai o último bit de cada um.
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    bit_len = payload_size_bytes * 8
    flat_image = image.flatten()

    # Pega apenas a quantidade necessária de bits
    extracted_bits = flat_image[:bit_len] & 1
    bits_str = ''.join(extracted_bits.astype(str))
    
    bytes_arr = bytearray()
    for i in range(0, bit_len, 8):
        bytes_arr.append(int(bits_str[i:i+8], 2))
        
    return bytes_arr

def compare_histograms(img1_path, img2_path, output_path="histograma_lsb.png"):
    """
    Gera um histograma comparando a imagem original com a esteganografada via LSB.
    """
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        print("Erro: Uma das imagens para o histograma não foi encontrada.")
        return

    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.title('Histograma - Capa (Original)')
    hist1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
    plt.plot(hist1, color='gray')
    plt.xlim([0, 256])

    plt.subplot(1, 2, 2)
    plt.title('Histograma - LSB (Estego)')
    hist2 = cv2.calcHist([img2], [0], None, [256], [0, 256])
    plt.plot(hist2, color='gray')
    plt.xlim([0, 256])

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

# ---------------------------------------------------------
# Testes Automáticos Pytest (Conforme Seção 3.3.3 do TCC)
# ---------------------------------------------------------

def setup_test_image_lsb():
    # Cria uma imagem PNG em escala de cinza para os testes (formato da BOSSBase)
    if not os.path.exists("test_capa_lsb.png"):
        img = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
        cv2.imwrite("test_capa_lsb.png", img)

def test_ida_e_volta_lsb():
    """ 1. O payload extraído tem o mesmo SHA-256 do original """
    setup_test_image_lsb()
    payload = os.urandom(131) # Payload de baixa taxa (131 bytes)
    hash_original = hashlib.sha256(payload).hexdigest()
    
    encode_lsb("test_capa_lsb.png", payload, "test_estego_lsb.png")
    
    payload_extraido = decode_lsb("test_estego_lsb.png", len(payload))
    hash_extraido = hashlib.sha256(payload_extraido).hexdigest()
    
    assert hash_original == hash_extraido, "Falha: O hash do arquivo extraído é diferente!"

def test_alteracao_minima_lsb():
    """ 2. Só os primeiros n pixels podem mudar, e no máximo em 1 ponto """
    setup_test_image_lsb()
    payload = os.urandom(50)
    n_bits = len(payload) * 8
    encode_lsb("test_capa_lsb.png", payload, "test_estego_lsb.png")
    
    im_capa = cv2.imread("test_capa_lsb.png", cv2.IMREAD_GRAYSCALE).flatten().astype(np.int16)
    im_estego = cv2.imread("test_estego_lsb.png", cv2.IMREAD_GRAYSCALE).flatten().astype(np.int16)
    
    diferenca = im_estego - im_capa
    
    # Valida que todos os pixels após o payload ficaram EXATAMENTE iguais
    assert np.all(diferenca[n_bits:] == 0), "Falha: Pixels fora da região do payload foram alterados!"
    
    # Valida que na região do payload, a alteração foi de NO MÁXIMO 1 (-1, 0 ou 1)
    alteracoes = diferenca[:n_bits]
    assert np.all(np.abs(alteracoes) <= 1), "Falha: A substituição LSB alterou um pixel em mais de 1 ponto de brilho!"

def test_protecao_capacidade_lsb():
    """ 3. Payload maior que a capacidade gera erro em vez de cortar em silêncio """
    setup_test_image_lsb()
    # Tenta embutir payload muito maior que a quantidade de pixels
    # 256x256 pixels = 65536 bits suportados. Um payload de 10.000 bytes = 80.000 bits.
    payload_gigante = os.urandom(10000)
    
    try:
        encode_lsb("test_capa_lsb.png", payload_gigante, "test_estego_lsb.png")
        assert False, "O código deveria ter gerado ValueError por falta de capacidade."
    except ValueError:
        pass # Comportamento correto!

if __name__ == "__main__":
    print("Executando módulo principal LSB...")
    setup_test_image_lsb()
    
    # Simulando um payload de dados inerte
    payload_teste = b"Este e um teste LSB para o TCC! " * 5
    print(f"Payload gerado ({len(payload_teste)} bytes).")
    
    encode_lsb("test_capa_lsb.png", payload_teste, "test_estego_lsb.png")
    print("Ocultação concluída (salva em test_estego_lsb.png).")
    
    payload_recuperado = decode_lsb("test_estego_lsb.png", len(payload_teste))
    print(f"Recuperação concluída: {payload_recuperado[:30]}...")
    
    # Etapa de análise visual
    compare_histograms("test_capa_lsb.png", "test_estego_lsb.png")
    print("Histograma gerado em 'histograma_lsb.png'.")