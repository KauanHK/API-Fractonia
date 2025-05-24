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

| Endpoint           | Método |
| ------------------ | ------ |
| `/auth/login`      | POST   |
| `/player/all`      | GET    |
| `/player/<int:id>` | GET    |
| `/item/all`        | GET    |
| `/phase/all`       | GET    |
| `/boss/all`        | GET    |
| `/rarity/all`      | GET    |
| ...                | ...    |

---

## 🛠️ Tecnologias utilizadas

* Python
* Flask
* SQLAlchemy
* Alembic (migrations)
