"""
Utilitários para sanitização de headers HTTP
"""
from typing import Optional


def sanitize_header_value(value: Optional[str]) -> str:
    """
    Sanitiza valor para header HTTP (remove quebras de linha e caracteres inválidos)
    
    Headers HTTP devem conter apenas caracteres ASCII (latin-1).
    Remove emojis e caracteres Unicode problemáticos, mas preserva acentos latinos.
    
    Args:
        value: Valor original
        
    Returns:
        Valor sanitizado seguro para headers HTTP (latin-1 compatível)
    """
    if not value:
        return ""
    
    # Remove quebras de linha e caracteres de controle
    sanitized = value.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    # Remove múltiplos espaços
    sanitized = " ".join(sanitized.split())
    
    # Remove caracteres que não podem ser codificados em latin-1
    # Preserva acentos latinos (á, é, í, ó, ú, ç, etc) que são válidos em latin-1
    sanitized_ascii = ""
    for char in sanitized:
        try:
            # Tenta codificar em latin-1 (se conseguir, é válido)
            # Isso preserva acentos latinos mas remove emojis e Unicode extenso
            char.encode('latin-1')
            sanitized_ascii += char
        except UnicodeEncodeError:
            # Caractere não compatível com latin-1 (emoji, Unicode extenso): substitui por espaço
            sanitized_ascii += " "
    
    # Remove múltiplos espaços novamente após remoção de Unicode
    sanitized_ascii = " ".join(sanitized_ascii.split())
    
    # Limita tamanho (headers HTTP têm limite prático)
    if len(sanitized_ascii) > 200:
        sanitized_ascii = sanitized_ascii[:197] + "..."
    
    return sanitized_ascii

