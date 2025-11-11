

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

"""
Gerenciador de Tarefas - Projeto Final

Descrição:
    Sistema de gerenciamento de tarefas com persistência em JSON.
    Suporta criação, edição, conclusão, arquivamento e relatórios.

Autores:
    Matheus Bertorini
    Matheus Alves

Funcionalidades:
    - Criação de tarefas com prioridade (urgente, alta, média, baixa)
    - Persistência em tarefas.json e tarefas_arquivadas.json
    - Validação de entrada com try/except
    - Relatórios completos
    - Menu interativo com 10 opções
"""

# === 11. VARIÁVEIS GLOBAIS (com controle de ID único) ===
tarefas: List[Dict] = []
proximo_id: int = 1
ARQUIVO_TAREFAS = "tarefas.json"
ARQUIVO_ARQUIVADAS = "tarefas_arquivadas.json"


# === 15. CRIAÇÃO AUTOMÁTICA DE ARQUIVOS ===
def inicializar_arquivos() -> None:
    """Verifica e cria arquivos JSON necessários com estrutura inicial."""
    print("Executando a função inicializar_arquivos")
    # Agora cria com estrutura completa para evitar erros futuros
    arquivos = {
        ARQUIVO_TAREFAS: {"tarefas": [], "proximo_id": 1},
        ARQUIVO_ARQUIVADAS: []
    }
    for arquivo, conteudo_inicial in arquivos.items():
        if not os.path.exists(arquivo):
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(conteudo_inicial, f, indent=2, ensure_ascii=False)
            print(f"Arquivo criado: {arquivo}")


# === 13. CARREGAR TAREFAS DO ARQUIVO (CORRIGIDO) ===
def carregar_tarefas() -> None:
    """Carrega tarefas de tarefas.json para a lista global, com compatibilidade."""
    global tarefas, proximo_id
    print("Executando a função carregar_tarefas")
    try:
        with open(ARQUIVO_TAREFAS, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        # CORREÇÃO: Verifica se é lista (versão antiga) ou dict (nova)
        if isinstance(dados, list):
            print("Detectado formato antigo (lista). Convertendo...")
            tarefas = dados
            proximo_id = max((t.get("id", 0) for t in tarefas), default=0) + 1
        elif isinstance(dados, dict):
            tarefas = dados.get("tarefas", [])
            proximo_id = dados.get("proximo_id", 1)
            if tarefas:
                proximo_id = max((t.get("id", 0) for t in tarefas), default=0) + 1
        else:
            raise ValueError("Formato de dados inválido no JSON.")
        
        print(f"Carregadas {len(tarefas)} tarefas. Próximo ID: {proximo_id}")
        
    except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
        print(f"Erro ao carregar (usando dados vazios): {e}")
        tarefas = []
        proximo_id = 1


# === 13. SALVAR TAREFAS NO ARQUIVO ===
def salvar_tarefas() -> None:
    """Salva a lista de tarefas no arquivo JSON antes de sair."""
    global tarefas, proximo_id
    print("Executando a função salvar_tarefas")
    dados = {
        "tarefas": tarefas,
        "proximo_id": proximo_id
    }
    try:
        with open(ARQUIVO_TAREFAS, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False, default=str)
        print("Dados salvos com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar: {e}")


# === 14. ARQUIVAR TAREFA EM ARQUIVO SEPARADO ===
def arquivar_tarefa(tarefa: Dict) -> None:
    """Move uma tarefa para o arquivo de arquivadas."""
    print("Executando a função arquivar_tarefa")
    try:
        with open(ARQUIVO_ARQUIVADAS, 'r', encoding='utf-8') as f:
            arquivadas = json.load(f)
        if not isinstance(arquivadas, list):
            arquivadas = []
    except (json.JSONDecodeError, FileNotFoundError):
        arquivadas = []

    arquivadas.append(tarefa)
    with open(ARQUIVO_ARQUIVADAS, 'w', encoding='utf-8') as f:
        json.dump(arquivadas, f, indent=2, ensure_ascii=False, default=str)


# === FUNÇÕES AUXILIARES DE VALIDAÇÃO ===
def obter_opcoes(mensagem: str, opcoes_validas: List[str]) -> str:
    """Valida entrada do usuário contra lista de opções."""
    print("Executando a função obter_opcoes")
    opcoes_str = ", ".join(opcoes_validas)
    while True:
        valor = input(f"{mensagem} ({opcoes_str}): ").strip().title()
        if valor in opcoes_validas:
            return valor
        print("Opção inválida. Tente novamente.")

def obter_texto_obrigatorio(mensagem: str) -> str:
    """Garante campo obrigatório."""
    print("Executando a função obter_texto_obrigatorio")
    while True:
        valor = input(f"{mensagem}: ").strip()
        if valor:
            return valor
        print("Este campo é obrigatório.")

def obter_texto_opcional(mensagem: str) -> str:
    """Permite campo opcional."""
    print("Executando a função obter_texto_opcional")
    return input(f"{mensagem} (opcional): ").strip()


# === 1. CRIAÇÃO DE TAREFA ===
def criar_tarefa() -> None:
    """Cria nova tarefa com validação e ID único."""
    print("Executando a função criar_tarefa")
    global proximo_id

    titulo = obter_texto_obrigatorio("Título")
    descricao = obter_texto_opcional("Descrição")
    prioridade = obter_opcoes("Prioridade", ["Urgente", "Alta", "Média", "Baixa"])
    

    nova_tarefa = {
        "id": proximo_id,
        "titulo": titulo,
        "descricao": descricao,
        "prioridade": prioridade,
        "status": "Pendente",
        "data_criacao": datetime.now().isoformat(),
        "data_conclusao": None
    }
    tarefas.append(nova_tarefa)
    proximo_id += 1
    print(f"Tarefa '{titulo}' criada com sucesso! ID: {nova_tarefa['id']}")


# === 2. PRÓXIMA TAREFA POR PRIORIDADE ===
def obter_proxima_tarefa() -> Optional[Dict]:
    """Seleciona próxima tarefa pendente por prioridade."""
    print("Executando a função obter_proxima_tarefa")
    prioridades = ["Urgente", "Alta", "Média", "Baixa"]
    pendentes = [t for t in tarefas if t["status"] == "Pendente"]

    if not pendentes:
        print("Nenhuma tarefa pendente.")
        return None

    for prio in prioridades:
        tarefas_prio = [t for t in pendentes if t["prioridade"] == prio]
        if tarefas_prio:
            proxima = tarefas_prio[0]
            proxima["status"] = "Fazendo"
            print(f"Tarefa selecionada: {proxima['titulo']} (Prioridade: {prio})")
            return proxima
    return None


# === 3. ATUALIZAR PRIORIDADE ===
def atualizar_prioridade(tarefa_id: int) -> None:
    """Altera prioridade de uma tarefa."""
    print("Executando a função atualizar_prioridade")
    tarefa = buscar_tarefa_por_id(tarefa_id)
    if not tarefa:
        return
    nova_prioridade = obter_opcoes("Nova prioridade", ["Urgente", "Alta", "Média", "Baixa"])
    tarefa["prioridade"] = nova_prioridade
    print("Prioridade atualizada!")


# === 4. CONCLUIR TAREFA ===
def concluir_tarefa(tarefa_id: int) -> None:
    """Marca tarefa como concluída."""
    print("Executando a função concluir_tarefa")
    tarefa = buscar_tarefa_por_id(tarefa_id)
    if not tarefa or tarefa["status"] != "Fazendo":
        print("Tarefa não encontrada ou não está em execução.")
        return
    tarefa["status"] = "Concluída"
    tarefa["data_conclusao"] = datetime.now().isoformat()
    print(f"Tarefa '{tarefa['titulo']}' concluída!")


# === 5. ARQUIVAR TAREFAS ANTIGAS (com cópia para arquivo) ===
def arquivar_tarefas_antigas() -> None:
    """Move tarefas concluídas há +7 dias para arquivadas."""
    print("Executando a função arquivar_tarefas_antigas")
    limite = datetime.now() - timedelta(days=7)
    arquivadas = 0

    for tarefa in tarefas[:]:
        if (tarefa["status"] == "Concluída" and
            tarefa["data_conclusao"] and
            datetime.fromisoformat(tarefa["data_conclusao"]) < limite):
            arquivar_tarefa(tarefa.copy())
            tarefas.remove(tarefa)
            arquivadas += 1

    print(f"{arquivadas} tarefa(s) arquivada(s).")


# === 6. EXCLUSÃO LÓGICA (com arquivamento) ===
def excluir_tarefa(tarefa_id: int) -> None:
    """Marca tarefa como Excluída e arquiva."""
    print("Executando a função excluir_tarefa")
    tarefa = buscar_tarefa_por_id(tarefa_id)
    if not tarefa or tarefa["status"] in ["Concluída", "Arquivado"]:
        print("Tarefa inválida ou já finalizada.")
        return
    tarefa["status"] = "Excluída"
    arquivar_tarefa(tarefa.copy())
    tarefas.remove(tarefa)
    print(f"Tarefa excluída logicamente.")


# === 7. RELATÓRIO DETALHADO ===
def exibir_relatorio_tarefa(tarefa_id: int) -> None:
    """Mostra todos os dados da tarefa."""
    print("Executando a função exibir_relatorio_tarefa")
    tarefa = buscar_tarefa_por_id(tarefa_id)
    if not tarefa:
        return

    print("\n" + "="*50)
    print(f"RELATÓRIO DA TAREFA - ID: {tarefa['id']}")
    print("="*50)
    print(f"Título: {tarefa['titulo']}")
    print(f"Descrição: {tarefa['descricao'] or 'Não informada'}")
    print(f"Prioridade: {tarefa['prioridade']}")
    print(f"Status: {tarefa['status']}")
    print(f"Origem: {tarefa['origem']}")
    print(f"Criação: {datetime.fromisoformat(tarefa['data_criacao']).strftime('%d/%m/%Y %H:%M')}")

    if tarefa["data_conclusao"]:
        conclusao = datetime.fromisoformat(tarefa["data_conclusao"])
        print(f"Conclusão: {conclusao.strftime('%d/%m/%Y %H:%M')}")
        tempo = conclusao - datetime.fromisoformat(tarefa['data_criacao'])
        horas = int(tempo.total_seconds() // 3600)
        minutos = int((tempo.total_seconds() % 3600) // 60)
        print(f"Tempo de execução: {horas}h {minutos}min")
    print("="*50)


# === 8. RELATÓRIO ARQUIVADAS ===
def exibir_relatorio_arquivados() -> None:
    """Lista tarefas arquivadas."""
    print("Executando a função exibir_relatorio_arquivados")
    try:
        with open(ARQUIVO_ARQUIVADAS, 'r', encoding='utf-8') as f:
            arquivadas = json.load(f)
        if not isinstance(arquivadas, list):
            arquivadas = []
    except:
        arquivadas = []

    if not arquivadas:
        print("\nNenhuma tarefa arquivada.")
        return

    print(f"\n{'='*60}")
    print(f"TAREFAS ARQUIVADAS ({len(arquivadas)})")
    print(f"{'='*60}")
    for t in arquivadas:
        status = t.get("status", "Desconhecido")
        data = t["data_conclusao"] or t["data_criacao"]
        data_str = datetime.fromisoformat(data).strftime('%d/%m/%Y')
        print(f"ID: {t['id']} | {t['titulo']} | {status} em {data_str}")
    print(f"{'='*60}")


# === FUNÇÃO UTILITÁRIA ===
def buscar_tarefa_por_id(tarefa_id: int) -> Optional[Dict]:
    """Busca tarefa por ID."""
    print("Executando a função buscar_tarefa_por_id")
    for tarefa in tarefas:
        if tarefa["id"] == tarefa_id:
            return tarefa
    print(f"Tarefa com ID {tarefa_id} não encontrada.")
    return None

def listar_tarefas_ativas() -> None:
    """Lista tarefas pendentes e em execução."""
    print("Executando a função listar_tarefas_ativas")
    ativas = [t for t in tarefas if t["status"] in ["Pendente", "Fazendo"]]
    if not ativas:
        print("\nNenhuma tarefa ativa.")
        return
    print("\nTAREFAS ATIVAS:")
    for t in ativas:
        print(f"[{t['id']}] {t['titulo']} - {t['status']} ({t['prioridade']})")


# === 1. MENU PRINCIPAL (com validação) ===
def menu() -> None:
    """Menu central com todas as opções e validação."""
    print("Executando a função menu")
    while True:
        print("\n" + "="*50)
        print("GERENCIADOR DE TAREFAS")
        print("="*50)
        print("1. Criar nova tarefa")
        print("2. Pegar próxima tarefa")
        print("3. Atualizar prioridade")
        print("4. Concluir tarefa")
        print("5. Arquivar tarefas antigas")
        print("6. Excluir tarefa")
        print("7. Relatório de tarefa")
        print("8. Relatório de arquivadas")
        print("9. Listar tarefas ativas")
        print("0. Sair")
        print("="*50)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            criar_tarefa()
        elif opcao == "2":
            obter_proxima_tarefa()
        elif opcao == "3":
            try:
                tid = int(input("ID da tarefa: "))
                atualizar_prioridade(tid)
            except ValueError:
                print("ID inválido.")
        elif opcao == "4":
            try:
                tid = int(input("ID da tarefa: "))
                concluir_tarefa(tid)
            except ValueError:
                print("ID inválido.")
        elif opcao == "5":
            arquivar_tarefas_antigas()
        elif opcao == "6":
            try:
                tid = int(input("ID da tarefa: "))
                excluir_tarefa(tid)
            except ValueError:
                print("ID inválido.")
        elif opcao == "7":
            try:
                tid = int(input("ID da tarefa: "))
                exibir_relatorio_tarefa(tid)
            except ValueError:
                print("ID inválido.")
        elif opcao == "8":
            exibir_relatorio_arquivados()
        elif opcao == "9":
            listar_tarefas_ativas()
        elif opcao == "0":
            print("Salvando dados e saindo...")
            salvar_tarefas()
            exit()
        else:
            print("Opção inválida. Tente novamente.")


# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    inicializar_arquivos()
    carregar_tarefas()

    menu()

