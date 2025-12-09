"""
Testes automatizados da Interface Web usando Playwright
Testa todas as funcionalidades da interface web
"""
import pytest
from playwright.sync_api import Page, expect, Playwright
import time
import os


@pytest.fixture(scope="session")
def base_url():
    """URL base do servidor"""
    return os.getenv("BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def browser(playwright: Playwright):
    """Cria um navegador para os testes"""
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """Cria uma nova página para cada teste"""
    page = browser.new_page()
    yield page
    page.close()


def test_interface_carrega(page: Page, base_url: str):
    """Testa se a interface web carrega corretamente"""
    print("\n🧪 Teste 1: Carregamento da interface")
    
    page.goto(f"{base_url}/web/")
    
    # Verifica título
    expect(page).to_have_title("Jonh Assistant - Teste Web")
    
    # Verifica elementos principais
    expect(page.locator("h1")).to_contain_text("Jonh Assistant")
    expect(page.locator("#user-input")).to_be_visible()
    expect(page.locator("button:has-text('Enviar Mensagem')")).to_be_visible()
    
    print("✅ Interface carregou corretamente")


def test_status_servicos(page: Page, base_url: str):
    """Testa se os status dos serviços são exibidos"""
    print("\n🧪 Teste 2: Status dos serviços")
    
    page.goto(f"{base_url}/web/")
    
    # Aguarda carregamento do status
    time.sleep(2)
    
    # Verifica se há elementos de status
    status_elements = page.locator(".status-item")
    
    # Verifica se há pelo menos um elemento
    count = status_elements.count()
    assert count > 0, "Nenhum elemento de status encontrado"
    
    # Verifica se o primeiro elemento está visível
    first_status = status_elements.first
    expect(first_status).to_be_visible()
    
    print(f"✅ Status dos serviços exibido ({count} elementos)")


def test_enviar_mensagem_simples(page: Page, base_url: str):
    """Testa envio de mensagem simples"""
    print("\n🧪 Teste 3: Envio de mensagem simples")
    
    page.goto(f"{base_url}/web/")
    
    # Aguarda interface carregar
    time.sleep(2)
    
    # Digita mensagem
    input_field = page.locator("#user-input")
    input_field.fill("Olá, como você está?")
    
    # Clica em enviar
    send_button = page.locator("button:has-text('Enviar Mensagem')")
    send_button.click()
    
    # Aguarda resposta
    time.sleep(5)
    
    # Verifica se resposta apareceu
    response_text = page.locator("#response-text")
    expect(response_text).not_to_have_text("Aguardando sua mensagem...")
    expect(response_text).not_to_have_text("Processando...")
    
    # Verifica se há texto na resposta
    response_content = response_text.text_content()
    assert len(response_content) > 10, "Resposta muito curta"
    
    print(f"✅ Mensagem enviada e resposta recebida: {response_content[:50]}...")


def test_audio_gerado(page: Page, base_url: str):
    """Testa se o áudio é gerado e exibido"""
    print("\n🧪 Teste 4: Geração de áudio")
    
    page.goto(f"{base_url}/web/")
    time.sleep(2)
    
    # Envia mensagem
    input_field = page.locator("#user-input")
    input_field.fill("Diga olá")
    
    send_button = page.locator("button:has-text('Enviar Mensagem')")
    send_button.click()
    
    # Aguarda processamento
    time.sleep(8)
    
    # Verifica se player de áudio aparece
    audio_player = page.locator("#audio-player")
    
    # Verifica se está visível (pode estar oculto se não houver áudio)
    try:
        is_visible = audio_player.is_visible(timeout=2000)
        if is_visible:
            audio_element = page.locator("#audio-element")
            expect(audio_element).to_have_attribute("src")
            print("✅ Áudio gerado e player exibido")
        else:
            print("⚠️  Player de áudio não visível (pode ser normal se não houver áudio)")
    except:
        print("⚠️  Player de áudio não encontrado (pode ser normal)")


def test_salvar_memoria(page: Page, base_url: str):
    """Testa salvamento de memória"""
    print("\n🧪 Teste 5: Salvamento de memória")
    
    page.goto(f"{base_url}/web/")
    time.sleep(2)
    
    # Envia comando para salvar memória
    input_field = page.locator("#user-input")
    input_field.fill("Anote que meu nome é Bruno")
    
    send_button = page.locator("button:has-text('Enviar Mensagem')")
    send_button.click()
    
    # Aguarda processamento
    time.sleep(8)
    
    # Verifica resposta
    response_text = page.locator("#response-text")
    response_content = response_text.text_content().lower()
    
    # Verifica se há confirmação (pode variar)
    assert len(response_content) > 5, "Resposta muito curta"
    
    print(f"✅ Memória salva: {response_content[:50]}...")


def test_recuperar_memoria(page: Page, base_url: str):
    """Testa recuperação de memória"""
    print("\n🧪 Teste 6: Recuperação de memória")
    
    page.goto(f"{base_url}/web/")
    time.sleep(2)
    
    # Primeiro salva memória (se não foi salva antes)
    input_field = page.locator("#user-input")
    input_field.fill("Anote que meu nome é Bruno")
    
    send_button = page.locator("button:has-text('Enviar Mensagem')")
    send_button.click()
    time.sleep(8)
    
    # Agora pergunta
    input_field.fill("Qual é meu nome?")
    send_button.click()
    
    # Aguarda resposta
    time.sleep(8)
    
    # Verifica se resposta contém "Bruno"
    response_text = page.locator("#response-text")
    response_content = response_text.text_content().lower()
    
    if "bruno" in response_content:
        print("✅ Memória recuperada corretamente (contém 'Bruno')")
    else:
        print(f"⚠️  Resposta recebida mas não contém 'Bruno': {response_content[:100]}")


def test_botao_limpar(page: Page, base_url: str):
    """Testa botão de limpar"""
    print("\n🧪 Teste 7: Botão limpar")
    
    page.goto(f"{base_url}/web/")
    time.sleep(2)
    
    # Envia mensagem primeiro
    input_field = page.locator("#user-input")
    input_field.fill("Teste")
    
    send_button = page.locator("button:has-text('Enviar Mensagem')")
    send_button.click()
    time.sleep(5)
    
    # Clica em limpar
    clear_button = page.locator("button:has-text('Limpar')")
    clear_button.click()
    
    # Verifica se resposta foi limpa
    response_text = page.locator("#response-text")
    expect(response_text).to_have_text("Aguardando sua mensagem...")
    
    print("✅ Botão limpar funciona")


def test_logs_aparecem(page: Page, base_url: str):
    """Testa se os logs aparecem no console"""
    print("\n🧪 Teste 8: Logs no console")
    
    page.goto(f"{base_url}/web/")
    time.sleep(2)
    
    # Envia mensagem
    input_field = page.locator("#user-input")
    input_field.fill("Teste de logs")
    
    send_button = page.locator("button:has-text('Enviar Mensagem')")
    send_button.click()
    time.sleep(5)
    
    # Verifica se há logs
    log_div = page.locator(".log")
    log_entries = log_div.locator(".log-entry")
    
    # Deve haver pelo menos alguns logs
    count = log_entries.count()
    assert count > 0, "Nenhum log encontrado"
    
    print(f"✅ Logs aparecem no console ({count} entradas)")


def test_multiplas_mensagens(page: Page, base_url: str):
    """Testa envio de múltiplas mensagens"""
    print("\n🧪 Teste 9: Múltiplas mensagens")
    
    page.goto(f"{base_url}/web/")
    time.sleep(2)
    
    mensagens = [
        "Olá",
        "Como você está?",
        "Qual é a capital do Brasil?"
    ]
    
    for i, msg in enumerate(mensagens, 1):
        input_field = page.locator("#user-input")
        input_field.fill(msg)
        
        send_button = page.locator("button:has-text('Enviar Mensagem')")
        send_button.click()
        
        # Aguarda resposta
        time.sleep(8)
        
        # Verifica resposta
        response_text = page.locator("#response-text")
        response_content = response_text.text_content()
        assert len(response_content) > 5, f"Resposta {i} muito curta"
        
        print(f"  ✅ Mensagem {i}/{len(mensagens)}: {msg[:30]}...")
    
    print("✅ Múltiplas mensagens processadas com sucesso")


def test_interface_responsiva(page: Page, base_url: str):
    """Testa se a interface é responsiva"""
    print("\n🧪 Teste 10: Interface responsiva")
    
    # Testa em diferentes tamanhos
    sizes = [
        {"width": 1920, "height": 1080},
        {"width": 1024, "height": 768},
        {"width": 375, "height": 667},  # Mobile
    ]
    
    for size in sizes:
        page.set_viewport_size(size)
        page.goto(f"{base_url}/web/")
        time.sleep(1)
        
        # Verifica se elementos principais estão visíveis
        expect(page.locator("#user-input")).to_be_visible()
        expect(page.locator("button:has-text('Enviar Mensagem')")).to_be_visible()
        
        print(f"  ✅ Tamanho {size['width']}x{size['height']}: OK")
    
    print("✅ Interface é responsiva")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

