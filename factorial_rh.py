import requests
import pandas as pd
import inquirer
import holidays
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# === CONFIGURAÇÕES ===
BASE_URL = 'https://api.factorialhr.com'

def carregar_api_key():
    """Carrega a API key do .env. Se não existir, pede ao utilizador e guarda no .env."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv('FACTORIAL_API_KEY')

    if not api_key:
        print("\n⚠️  Ficheiro .env não encontrado ou FACTORIAL_API_KEY não definida.")
        resposta = inquirer.prompt([
            inquirer.Text('chave', message="🔑 Introduz a tua API Key do Factorial HR")
        ])
        api_key = resposta['chave'].strip()

        if not api_key:
            raise ValueError("❌ Nenhuma API Key introduzida. O programa não pode continuar.")

        # Guardar no .env
        with open(env_path, 'a') as f:
            f.write(f"\nFACTORIAL_API_KEY={api_key}\n")
        print(f"✅ API Key guardada em: {env_path}")

    return api_key

API_KEY = carregar_api_key()

headers = {
    'x-api-key': API_KEY,
    'accept': 'application/json'
}

# === UTILITÁRIOS ===

def formatar_data(data_input) -> str:
    """
    Aceita string 'YYYY-MM-DD' ou objeto datetime e devolve 'DD/MM/YYYY'.
    Se não reconhecer, devolve string original.
    """
    if not data_input:
        return ''
    if isinstance(data_input, datetime):
        return data_input.strftime("%d/%m/%Y")
    try:
        # espera 'YYYY-MM-DD'
        return datetime.strptime(str(data_input), "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return str(data_input)


feriados_pt = holidays.country_holidays('PT')


def calcular_dias_uteis(inicio_str: str, fim_str: str):
    try:
        inicio = datetime.strptime(inicio_str, "%Y-%m-%d")
        fim = datetime.strptime(fim_str, "%Y-%m-%d")
        dias_uteis = sum(
            1
            for dia in (inicio + timedelta(n) for n in range((fim - inicio).days + 1))
            if dia.weekday() < 5 and dia not in feriados_pt
        )
        return dias_uteis
    except Exception:
        return ''


# === FUNÇÕES DE API ===

def obter_colaboradores_dict():
    """
    Retorna um dicionário com:
    {
        employee_id: {
            'full_name': str,
            'email': str,
            'manager_id': int (ou None)
        }
    }
    """
    url = f'{BASE_URL}/api/2026-01-01/resources/employees/employees'
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Erro ao obter colaboradores: {resp.status_code} - {resp.text}")
        return {}
    
    colaboradores = {}
    for c in resp.json().get('data', []):
        colaboradores[c.get('id')] = {
            'active': c.get('active', ''),
            'full_name': c.get('full_name', 'Desconhecido'),
            'email': c.get('email', ''),
            'manager_id': c.get('manager_id')
        }
    return colaboradores

# === TIPOS DE AUSÊNCIAS ===

def obter_tipos_ausencia():
    url = f'{BASE_URL}/api/2026-01-01/resources/timeoff/leave_types'
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Erro ao obter tipos de ausência: {resp.status_code} - {resp.text}")
        return {}
    return {t.get('id'): t.get('translated_name') for t in resp.json().get('data', [])}


# === AUSÊNCIAS ===

def listar_ausencias_avancado():
    colaboradores = obter_colaboradores_dict()
    tipos_ausencia = obter_tipos_ausencia()

    if not colaboradores:
        print("Erro ao obter colaboradores.")
        return []

    if not tipos_ausencia:
        print("Erro ao obter tipos de ausência.")
        return []

    filtros = {}

    # Filtro por colaborador
    nomes = [(info['full_name'], str(cid)) for cid, info in colaboradores.items()]
    nomes.insert(0, ("👥 Todos os funcionários", "todos"))
    escolha_colab = inquirer.prompt([
        inquirer.List("colab", message="👤 Escolha o colaborador", choices=nomes)
    ])
    if escolha_colab["colab"] != "todos":
        filtros["employee_ids[]"] = escolha_colab["colab"]

    # Filtro por período
    periodo = inquirer.prompt([
        inquirer.List(
            "periodo",
            message="📅 Período das ausências",
            choices=[
                ("🗓️ Mês atual", "mes_atual"),
                ("📆 Todas as datas", "todas"),
                ("📅 Inserir intervalo de datas", "intervalo"),
                ("🔙 Voltar", "voltar"),
            ],
        )
    ])["periodo"]

    if periodo == "voltar":
        return []

    limite_inicio = None
    limite_fim = None

    if periodo == "mes_atual":
        # Mês atual (do 1º ao último dia)
        hoje = datetime.today()
        primeiro_dia = hoje.replace(day=1)
        proximo_mes = (primeiro_dia.replace(day=28) + timedelta(days=4)).replace(day=1)
        ultimo_dia = proximo_mes - timedelta(days=1)
        limite_inicio = primeiro_dia
        limite_fim = ultimo_dia
        print(f"📅 Período selecionado: {limite_inicio.strftime('%d/%m/%Y')} a {limite_fim.strftime('%d/%m/%Y')}")

    elif periodo == "intervalo":
        datas = inquirer.prompt([
            inquirer.Text("inicio", message="📅 Data de início (DD-MM-YYYY)"),
            inquirer.Text("fim", message="📅 Data de fim (DD-MM-YYYY)")
        ])
        # Converter de DD-MM-YYYY para YYYY-MM-DD
        try:
            limite_inicio = datetime.strptime(datas['inicio'], "%d-%m-%Y")
            limite_fim = datetime.strptime(datas['fim'], "%d-%m-%Y")
            filtros['start_on'] = limite_inicio.strftime('%Y-%m-%d')
            filtros['finish_on'] = limite_fim.strftime('%Y-%m-%d')
            print(f"📅 Período selecionado: {limite_inicio.strftime('%d/%m/%Y')} a {limite_fim.strftime('%d/%m/%Y')}")
        except ValueError:
            print("❌ Formato de data inválido. Use DD-MM-YYYY (ex: 01-12-2024)")
            return []

    # Filtro por estado
    estado = inquirer.prompt([
        inquirer.List(
            "estado",
            message="📌 Estado da ausência",
            choices=[
                ("📋 Todos", "todos"),
                ("✅ Aprovada", "approved"),
                ("❌ Rejeitada", "rejected"),
                ("⏳ Pendente", "pending"),
                ("🔙 Voltar", "voltar"),
            ],
        )
    ])['estado']

    if estado == "voltar":
        return []
    if estado != "todos":
        filtros['status'] = estado

    # Filtro por tipo
    tipos_lista = [(v, str(k)) for k, v in tipos_ausencia.items()]
    tipos_lista.insert(0, ("📋 Todos os tipos", "todos"))
    tipo_escolhido = inquirer.prompt([
        inquirer.List("tipo", message="📝 Tipo de ausência", choices=tipos_lista)
    ])['tipo']

    if tipo_escolhido != "todos":
        filtros['leave_type_ids[]'] = tipo_escolhido

    # Paginação: buscar todas as páginas
    url = f'{BASE_URL}/api/2026-01-01/resources/timeoff/leaves'
    ausencias = []
    pagina = 1

    while True:
        filtros['page'] = pagina
        resp = requests.get(url, headers=headers, params=filtros)

        if resp.status_code != 200:
            print(f"Erro ao obter ausências (página {pagina}): {resp.status_code} - {resp.text}")
            break

        dados_pagina = resp.json().get('data', [])
        if not dados_pagina:
            break

        ausencias.extend(dados_pagina)
        if len(dados_pagina) < 100:
            break

        pagina += 1

    dados = []
    for a in ausencias:
        emp_id = a.get('employee_id')
        tipo_id = a.get('leave_type_id')
        ausencia_id = a.get('id')
        inicio_raw = a.get('start_on')
        fim_raw = a.get('finish_on')

        if not inicio_raw or not fim_raw:
            continue

        inicio_dt = datetime.strptime(inicio_raw, "%Y-%m-%d")
        fim_dt = datetime.strptime(fim_raw, "%Y-%m-%d")

        # Determinar as datas efetivas a mostrar e a duração
        if limite_inicio and limite_fim:
            # Verifica se há sobreposição com o período selecionado
            if fim_dt < limite_inicio or inicio_dt > limite_fim:
                continue  # Não há sobreposição -> ignora

            # Corta a ausência aos limites do período
            inicio_efetivo = max(inicio_dt, limite_inicio)
            fim_efetivo = min(fim_dt, limite_fim)
            
            # As datas mostradas são as efetivas (dentro do intervalo)
            data_inicio_mostrar = inicio_efetivo
            data_fim_mostrar = fim_efetivo
            
            # Duração apenas dentro do intervalo (dias úteis)
            total_dias_uteis = calcular_dias_uteis(
                inicio_efetivo.strftime("%Y-%m-%d"),
                fim_efetivo.strftime("%Y-%m-%d"),
            )
        else:
            # Sem período definido (todas as datas): mostra e conta tudo
            data_inicio_mostrar = inicio_dt
            data_fim_mostrar = fim_dt
            total_dias_uteis = calcular_dias_uteis(inicio_raw, fim_raw)

        # Informações do colaborador
        info_emp = colaboradores.get(emp_id, {})
        status_emp = info_emp.get('active', '')
        nome_emp = info_emp.get('full_name', 'Desconhecido')
        email_emp = info_emp.get('email', '')
        manager_id = info_emp.get('manager_id')
        
        # Nome do supervisor
        supervisor_nome = ''
        if manager_id and manager_id in colaboradores:
            supervisor_nome = colaboradores[manager_id].get('full_name', '')

        # Duração (dias úteis ou horas)
        duracao_cent = a.get('hours_amount_in_cents')
        half_day = a.get('half_day', False)  # campo da API que indica meio dia

        if half_day:
            duracao_valor = 0.5
        elif duracao_cent:
            horas = duracao_cent / 100
            duracao_valor = f"{int(horas):02}:{int((horas % 1) * 60):02}"
        else:
            duracao_valor = total_dias_uteis

        # Hora/Dia (se for ausência parcial)
        start_time = a.get('start_time', '')
        half_day = a.get('half_day', False)

        if start_time:
            hora_dia = start_time  # hora específica (ex: "17:00")
        elif half_day or duracao_valor == 0.5:
            hora_dia = 'Meio dia'
        else:
            hora_dia = 'Dia completo'

        # URL da ausência
        url_ausencia = (
            f"https://app.factorialhr.com/employees/{emp_id}/time-off/leaves/edit/{ausencia_id}"
            if emp_id and ausencia_id else ''
        )

        dados.append({
            'Nome': nome_emp,
            'Estado': 'Ativo' if status_emp else 'Inativo',
            'E-mail': email_emp,
            'Supervisor': supervisor_nome,
            # Guardar objetos datetime para exportação correcta
            'Data de início': data_inicio_mostrar,
            'Data de fim': data_fim_mostrar,
            'Duração': duracao_valor,
            'Hora/Dia': hora_dia,
            'Aprovação': 'Aprovada' if a.get('approved') else 'Pendente/Rejeitada',
            'Tipo de ausência': tipos_ausencia.get(tipo_id, 'Desconhecido'),
            'Descrição': a.get('description') or '',
            'Link para a ausência': url_ausencia,
        })

    return dados


# === EXPORTAÇÃO ===

def resolver_conflito_ficheiro(caminho):
    """Se o ficheiro já existir, pergunta se substitui ou renomeia automaticamente com _v2, _v3..."""
    if not os.path.exists(caminho):
        return caminho

    opcao = inquirer.prompt([
        inquirer.List(
            "conflito",
            message=f"⚠️ O ficheiro já existe. O que pretende fazer?",
            choices=[
                ("🔄 Substituir", "substituir"),
                ("📋 Renomear automaticamente (_v2, _v3...)", "renomear"),
            ]
        )
    ])['conflito']

    if opcao == "substituir":
        return caminho

    # Renomear: encontrar a próxima versão disponível
    base, ext = os.path.splitext(caminho)
    # Remove sufixo _vN se já existir
    import re
    base = re.sub(r'_v\d+$', '', base)
    versao = 2
    while True:
        novo_caminho = f"{base}_v{versao}{ext}"
        if not os.path.exists(novo_caminho):
            return novo_caminho
        versao += 1

def exportar_para_excel(dados, nome_arquivo):
    df = pd.DataFrame(dados)

    # Garantir que as colunas de data são datetime (podem já ser)
    for col in ['Data de início', 'Data de fim']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Usar ExcelWriter para definir formato das células de data
    sheet_name = 'Ausencias'
    with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        date_format = 'DD/MM/YYYY'
        # localizar índices das colunas de data
        for col in ['Data de início', 'Data de fim']:
            if col in df.columns:
                col_idx = df.columns.get_loc(col)
                # escrever format para cada célula na coluna (evita problemas de dtype)
                for row in range(2, len(df) + 2):  # +2 => header + 1-based rows
                    cell = worksheet.cell(row=row, column=col_idx + 1)
                if cell.value is not None:
                    cell.number_format = date_format

        # Definir a coluna "Link para a ausência" como hiperligação
        if 'Link para a ausência' in df.columns:
            link_col_idx = df.columns.get_loc('Link para a ausência') + 1  # 1-based
            for row in range(2, len(df) + 2):
                cell = worksheet.cell(row=row, column=link_col_idx)
                url = cell.value
                if url:
                    cell.hyperlink = url
                    cell.style = "Hyperlink"

    print(f"\n✅ Dados exportados com sucesso para: {nome_arquivo}")


def criar_pasta(caminho):
    if not os.path.exists(caminho):
        os.makedirs(caminho)
        print(f"📁 Pasta criada: {caminho}")


# === MENU INTERATIVO - RECURSOS HUMANOS ===

def exibir_menu():
    print("\n" + "="*50)
    print("🏢 FACTORIAL HR - RECURSOS HUMANOS")
    print("="*50 + "\n")
    
    while True:
        resposta = inquirer.prompt([
            inquirer.List(
                "menu",
                message="📋 Menu Principal - RH",
                choices=[
                    "👤 Listar Colaboradores",
                    "📅 Listar Ausências",
                    "🚪 Sair",
                ],
            )
        ])

        opcao = resposta['menu']

        if opcao == "🚪 Sair":
            print("👋 A sair...")
            break

        if opcao == "📅 Listar Ausências":
            dados = listar_ausencias_avancado()
        elif opcao == "👤 Listar Colaboradores":
            from_main = obter_colaboradores_dict()
            dados = [{"ID": k, "Nome": v['full_name'], "Estado": 'Ativo' if v['active'] else 'Inativo', "E-mail": v['email']} for k, v in from_main.items()]
        else:
            continue

        if not dados:
            print("⚠️ Nenhum dado encontrado.")
            continue

        print(f"\n✅ {len(dados)} registos encontrados.")

        # Mostrar uma pré-visualização formatada (datas em dd/mm/aaaa)
        for item in dados[:5]:
            display_item = item.copy()
            for date_col in ['Data de início', 'Data de fim']:
                if date_col in display_item:
                    display_item[date_col] = formatar_data(display_item[date_col])
            print(display_item)

        exportar = inquirer.prompt([
            inquirer.Confirm("confirmar", message="💾 Exportar para Excel?", default=True)
        ])

        if exportar.get("confirmar"):
            pasta = inquirer.prompt([
                inquirer.List(
                    "onde",
                    message="📁 Guardar em...",
                    choices=["📂 Atual", "📁 Específica"],
                )
            ])['onde']

            nome_arquivo = inquirer.prompt([
                inquirer.Text("nome", message="📄 Nome do ficheiro")
            ])['nome'].strip()

            # Se o nome não tiver extensão, adiciona .xlsx
            if '.' not in nome_arquivo:
                nome_arquivo += ".xlsx"

            if pasta == "📂 Atual":
                caminho = os.path.join(os.getcwd(), nome_arquivo)
            else:
                caminho_pasta = inquirer.prompt([
                    inquirer.Text("pasta", message="📁 Caminho completo da pasta")
                ])['pasta'].strip()
                criar_pasta(caminho_pasta)
                caminho = os.path.join(caminho_pasta, nome_arquivo)

            caminho = resolver_conflito_ficheiro(caminho)
            exportar_para_excel(dados, caminho)


# === EXECUÇÃO ===

if __name__ == '__main__':
    exibir_menu()