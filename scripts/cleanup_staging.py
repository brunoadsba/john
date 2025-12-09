#!/usr/bin/env python3
"""
Script para limpar staging do Git, mantendo apenas arquivos essenciais
"""
import subprocess
import sys
import os

# Arquivos/diretórios que DEVEM ser commitados (essenciais)
ESSENTIAL_PATTERNS = [
    # Documentação principal
    'README.md',
    'PLAN.md',
    'QUICKSTART.md',
    'SECURITY.md',
    'LICENSE.txt',
    'CONTRIBUTING.md',
    
    # Estrutura do projeto
    'backend/api/',
    'backend/services/',
    'backend/config/',
    'backend/core/',
    'backend/plugins/',
    'backend/database/',
    'backend/tests/',
    'backend/requirements.txt',
    'backend/scripts/',
    
    # Mobile app
    'mobile_app/lib/',
    'mobile_app/android/',
    'mobile_app/ios/',
    'mobile_app/pubspec.yaml',
    'mobile_app/analysis_options.yaml',
    
    # Scripts essenciais
    'scripts/start_server.sh',
    'scripts/install_dependencies.sh',
    'scripts/test_playwright.sh',
    'scripts/check_mobile_config.sh',
    
    # Documentação essencial
    'docs/STATUS_PROJETO.md',
    'docs/ARQUITETURA.md',
    'docs/INSTALACAO.md',
    'docs/TROUBLESHOOTING.md',
    'docs/CRIAR_PLUGINS.md',
    'docs/FASE1_OTIMIZACAO_PERFORMANCE.md',
    'docs/FEATURE_019_IMPLEMENTACAO.md',
    'docs/FEATURE_020_IMPLEMENTACAO.md',
    'docs/FEATURE_021_IMPLEMENTACAO.md',
    'docs/FEATURE_022_IMPLEMENTACAO.md',
    
    # Configuração
    '.gitignore',
    '.cursor/rules',
    '.cursor/commands/',
]

# Arquivos que NÃO devem ser commitados (temporários/debug)
EXCLUDE_PATTERNS = [
    '*.bak',
    '*.tmp',
    '*_temp.md',
    '*_DEBUG.md',
    '*_TESTE.md',
    '*_TESTES.md',
    '*_RESUMO.md',
    '*_RELATORIO.md',
    '*_RESULTADO.md',
    '*_STATUS.md',
    '*_VERIFICACAO.md',
    '*_CORRECAO.md',
    '*_CORRECOES.md',
    '*_IMPLEMENTACAO.md',
    '*_IMPLEMENTACOES.md',
    '*_INTEGRACAO.md',
    '*_ANALISE.md',
    '*_AVALIACAO.md',
    '*_DIAGNOSTICO.md',
    '*_PROBLEMA.md',
    '*_SOLUCAO.md',
    '*_MIGRACAO.md',
    '*_REFATORACAO.md',
    '*_PENDENCIAS.md',
    '*_PLANO.md',
    '*_GUIA.md',
    '*_INSTRUCOES.md',
    'FEATURE_*.md',
    'APK_*.md',
    'BUILD_*.md',
    'teste_*.sh',
    'teste_*.py',
    '*.db',
    '*.sqlite',
    '=*.0',
    'backend/=*.0',
    'training_*.json',
    'headers.txt',
    'docs/_arquivados/',
]

def run_git_command(cmd):
    """Executa comando git"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar: {cmd}")
        print(f"Erro: {e.stderr}")
        return None

def get_staged_files():
    """Lista arquivos stageados"""
    output = run_git_command("git diff --cached --name-only")
    if not output:
        return []
    return output.split('\n')

def should_keep_file(filepath):
    """Verifica se arquivo deve ser mantido"""
    # Verifica padrões de exclusão
    for pattern in EXCLUDE_PATTERNS:
        if pattern.endswith('/'):
            if filepath.startswith(pattern):
                return False
        elif '*' in pattern:
            import fnmatch
            if fnmatch.fnmatch(filepath, pattern):
                return False
        elif filepath == pattern or filepath.endswith('/' + pattern):
            return False
    
    # Verifica padrões essenciais
    for pattern in ESSENTIAL_PATTERNS:
        if pattern.endswith('/'):
            if filepath.startswith(pattern):
                return True
        elif filepath == pattern or filepath.endswith('/' + pattern):
            return True
    
    # Arquivos de código fonte sempre mantém
    if any(filepath.startswith(p) for p in ['backend/', 'mobile_app/lib/', 'scripts/']):
        if not any(filepath.endswith(ext) for ext in ['.bak', '.tmp', '.db', '.log']):
            return True
    
    return False

def main():
    print("🔍 Analisando arquivos stageados...")
    staged_files = get_staged_files()
    
    if not staged_files:
        print("✅ Nenhum arquivo stageado encontrado.")
        return 0
    
    print(f"📦 Encontrados {len(staged_files)} arquivos stageados")
    
    files_to_remove = []
    files_to_keep = []
    
    for filepath in staged_files:
        if should_keep_file(filepath):
            files_to_keep.append(filepath)
        else:
            files_to_remove.append(filepath)
    
    print(f"\n✅ Arquivos a manter: {len(files_to_keep)}")
    print(f"🗑️  Arquivos a remover do staging: {len(files_to_remove)}")
    
    if files_to_remove:
        print("\n📋 Arquivos que serão removidos do staging:")
        for f in files_to_remove[:20]:  # Mostra primeiros 20
            print(f"  - {f}")
        if len(files_to_remove) > 20:
            print(f"  ... e mais {len(files_to_remove) - 20} arquivos")
    
    if files_to_remove:
        print("\n🔄 Removendo arquivos do staging...")
        for filepath in files_to_remove:
            run_git_command(f"git restore --staged '{filepath}'")
        print("✅ Staging limpo!")
    
    if files_to_keep:
        print(f"\n✅ Mantidos {len(files_to_keep)} arquivos essenciais no staging")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

