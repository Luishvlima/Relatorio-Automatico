import os
import requests

def main_telegram(caminho_da_imagem: str, token: str, chat_ids: list, log, mensagem: str) -> bool:
    if not os.path.exists(caminho_da_imagem):
        log.info(f"Arquivo não encontrado: {caminho_da_imagem}")
        return False
    
    Se_Tudo_Ok = True
    for cada_chat in chat_ids:
        try:
            _Enviar_foto(token, str(cada_chat).strip(), caminho_da_imagem, mensagem)
            log.info(f"Imagem enviada com sucesso para o chat_id {cada_chat}")

        except Exception as e:
            log.info(f"Erro {cada_chat}: {e}")
            Se_Tudo_Ok = False

    return Se_Tudo_Ok
        
def _Enviar_foto(token: str, chat_id: str, caminho_da_imagem: str, mensagem: str):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"

    with open(caminho_da_imagem, "rb") as imagem:
        response = requests.post(
            url,
            data={"chat_id": chat_id, "caption": mensagem},
            files={"photo": (os.path.basename(caminho_da_imagem), imagem, "image/jpeg")},
            timeout=40
        )

    try:
        res = response.json()
    except ValueError:
        response.raise_for_status()
        raise RuntimeError("Resposta inválida da API do Telegram")

    if not response.ok or not res.get("ok"):
        descricao = res.get("description", f"HTTP {response.status_code}")
        if "PHOTO_INVALID_DIMENSIONS" in descricao:
            
            _Enviar_documento(token, chat_id, caminho_da_imagem, mensagem)
            return
        raise RuntimeError(descricao)

def _Enviar_documento(token: str, chat_id: str, caminho_arquivo: str, mensagem: str):
    url = f"https://api.telegram.org/bot{token}/sendDocument"

    with open(caminho_arquivo, "rb") as arquivo:
        response = requests.post(
            url,
            data={"chat_id": chat_id, "caption": mensagem},
            files={"document": (os.path.basename(caminho_arquivo), arquivo, "application/octet-stream")},
            timeout=40
        )

    try:
        res = response.json()
    except ValueError:
        response.raise_for_status()
        raise RuntimeError("Resposta inválida da API do Telegram")

    if not response.ok or not res.get("ok"):
        descricao = res.get("description", f"HTTP {response.status_code}")
        raise RuntimeError(descricao)
