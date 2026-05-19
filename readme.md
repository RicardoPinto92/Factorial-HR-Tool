# 🏢 Factorial HR — Gestão de Ausências

> Ferramenta de linha de comandos para consultar e exportar dados de colaboradores e ausências a partir da API do [Factorial HR](https://factorialhr.com).

---

## 🇵🇹 Português

### Objetivo

Este programa permite às equipas de Recursos Humanos consultar, filtrar e exportar para Excel os dados de ausências e colaboradores registados no Factorial HR, diretamente a partir do terminal, sem necessidade de aceder à plataforma web.

### Funcionalidades

- 👤 Listar colaboradores com estado (Ativo / Inativo)
- 📅 Listar ausências com filtros por:
  - Colaborador
  - Período (mês atual, todas as datas ou intervalo personalizado)
  - Estado (Aprovada, Rejeitada, Pendente)
  - Tipo de ausência
- 📊 Exportar resultados para ficheiro Excel (`.xlsx`) com:
  - Datas formatadas em `DD/MM/YYYY`
  - Duração em dias úteis (excluindo feriados portugueses e fins de semana)
  - Indicação de meio dia ou hora específica
  - Estado de aprovação
  - Link direto para a ausência no Factorial HR
- ⚠️ Gestão de conflitos ao exportar (substituir ou renomear com `_v2`, `_v3`...)

### Pré-requisitos

```bash
pip install requests pandas inquirer holidays openpyxl python-dotenv
```

### Configuração

1. Cria um ficheiro `.env` na pasta do projeto:

```
FACTORIAL_API_KEY=a_tua_chave_aqui
```

> Se o ficheiro `.env` não existir, o programa irá pedir a chave ao iniciar e guardá-la automaticamente.

2. Obtém a tua API Key em: `Factorial HR → Definições → Integrações → API`

### Execução

```bash
python factorial_rh.py
```

---

## 🇬🇧 English

### Purpose

This command-line tool allows HR teams to query, filter, and export employee and leave data from Factorial HR directly from the terminal, without needing to access the web platform.

### Features

- 👤 List employees with status (Active / Inactive)
- 📅 List absences with filters by:
  - Employee
  - Period (current month, all dates, or custom range)
  - Status (Approved, Rejected, Pending)
  - Leave type
- 📊 Export results to Excel (`.xlsx`) with:
  - Dates formatted as `DD/MM/YYYY`
  - Duration in working days (excluding Portuguese public holidays and weekends)
  - Half-day or specific time indication
  - Approval status
  - Direct link to the leave in Factorial HR
- ⚠️ Export conflict management (replace or auto-rename with `_v2`, `_v3`...)

### Requirements

```bash
pip install requests pandas inquirer holidays openpyxl python-dotenv
```

### Setup

1. Create a `.env` file in the project folder:

```
FACTORIAL_API_KEY=your_api_key_here
```

> If the `.env` file does not exist, the program will prompt you for the key on startup and save it automatically.

2. Get your API Key at: `Factorial HR → Settings → Integrations → API`

### Run

```bash
python factorial_rh.py
```

---

## 🇫🇷 Français

### Objectif

Cet outil en ligne de commande permet aux équipes RH de consulter, filtrer et exporter vers Excel les données des collaborateurs et des absences enregistrées dans Factorial HR, directement depuis le terminal, sans avoir besoin d'accéder à la plateforme web.

### Fonctionnalités

- 👤 Lister les collaborateurs avec leur statut (Actif / Inactif)
- 📅 Lister les absences avec des filtres par :
  - Collaborateur
  - Période (mois en cours, toutes les dates ou plage personnalisée)
  - Statut (Approuvée, Rejetée, En attente)
  - Type d'absence
- 📊 Exporter les résultats vers un fichier Excel (`.xlsx`) avec :
  - Dates au format `DD/MM/YYYY`
  - Durée en jours ouvrables (hors jours fériés portugais et week-ends)
  - Indication demi-journée ou heure spécifique
  - Statut d'approbation
  - Lien direct vers l'absence dans Factorial HR
- ⚠️ Gestion des conflits à l'export (remplacer ou renommer automatiquement avec `_v2`, `_v3`...)

### Prérequis

```bash
pip install requests pandas inquirer holidays openpyxl python-dotenv
```

### Configuration

1. Créez un fichier `.env` dans le dossier du projet :

```
FACTORIAL_API_KEY=votre_clé_api_ici
```

> Si le fichier `.env` n'existe pas, le programme vous demandera la clé au démarrage et la sauvegardera automatiquement.

2. Obtenez votre clé API sur : `Factorial HR → Paramètres → Intégrations → API`

### Exécution

```bash
python factorial_rh.py
```

---

## 📁 Estrutura do Projeto / Project Structure / Structure du Projet

```
factorial_rh/
├── factorial_rh.py     # Script principal / Main script / Script principal
├── .env                # ⚠️ Não incluído no repositório / Not included in repo / Non inclus dans le dépôt
├── .env.example        # Exemplo de configuração / Config example / Exemple de configuration
├── .gitignore
└── README.md
```

---

## 🔐 Segurança / Security / Sécurité

A API Key **nunca deve ser partilhada nem incluída no repositório**.  
The API Key **must never be shared or included in the repository**.  
La clé API **ne doit jamais être partagée ni incluse dans le dépôt**.

O ficheiro `.env` está incluído no `.gitignore` por defeito.  
The `.env` file is included in `.gitignore` by default.  
Le fichier `.env` est inclus dans `.gitignore` par défaut.

---

## 📄 Licença / License / Licence

MIT
