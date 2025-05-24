# 🎮 API de Gerenciamento de Jogadores, Itens e Fases

Esta é uma API desenvolvida em Flask com SQLAlchemy para gerenciar jogadores, itens, fases, bosses e raridades em um ambiente de jogo.

## 🚀 Como instalar e executar a API

### 1. Clonar o repositório

```bash
git clone https://github.com/KauanHK/API-Fractonia.git
cd API-Fractonia
```

---

### 2. Criar ambiente virtual e ativá-lo

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

---

### 4. Configurar e aplicar as migrações do banco de dados

```bash
flask db init
flask db migrate
flask db upgrade
```

---

### 5. Inserir dados iniciais

```bash
flask insert-data
```

Esse comando executa um script SQL e insere alguns dados no banco.

---

### 6. Executar a API

```bash
flask run
```

A API estará disponível em:

```
http://127.0.0.1:5000/
```

---

## 📚 Estrutura de endpoints principais

| Método   | Endpoint                  |
| -------- | ------------------------- |
| POST     | /auth/login               |
| GET      | /boss/[id]                |
| GET      | /boss/all                 |
| POST     | /boss/new                 |
| GET      | /item/[id]                |
| GET      | /item/all                 |
| POST     | /item/new                 |
| POST     | /phase/new                |
| GET      | /phase/[id]               |
| GET      | /phase/all                |
| GET      | /player/all               |
| POST     | /player/[id]/new-item     |
| POST     | /player/new               |
| GET      | /player/[id]              |
| GET      | /player/[id]/items        |
| GET      | /player/[id]/stats        |
| POST     | /rarity/new               |
| GET      | /rarity/all               |
| GET      | /rarity/[id]              |

---

## 🛠️ Tecnologias utilizadas

* Python
* Flask
* SQLAlchemy
* Alembic (migrations)
