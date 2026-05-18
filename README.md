# FinIA – Contador Pessoal com Inteligência Artificial

Sistema web moderno de controle financeiro pessoal com IA integrada.

---

## Estrutura de Arquivos

```
finia/
├── app.py               ← Backend Flask (rotas, API, IA, chatbot)
├── database.db          ← Banco SQLite (criado automaticamente)
├── requirements.txt     ← Dependência: Flask
├── README.md
├── templates/
│   ├── layout.html      ← Template base (sidebar, topbar, toast)
│   ├── dashboard.html   ← Dashboard com cards e gráficos
│   ├── transacoes.html  ← CRUD completo de transações
│   ├── chatbot.html     ← Chat financeiro com IA
│   └── relatorios.html  ← Relatórios e exportação CSV
└── static/
    ├── css/style.css    ← Design dark mode completo
    └── js/script.js     ← Sidebar, toast, utilitários
```

---

## 1. Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip

### Passos

```bash
# 1. Entre na pasta do projeto
cd finia

# 2. (Opcional) Crie um ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instale a dependência
pip install -r requirements.txt
```

---

## 2. Como Executar

```bash
python app.py
```

Acesse no navegador: **http://localhost:5000**

O banco de dados é criado automaticamente com dados de exemplo.

---

## 3. Funcionalidades

### Dashboard (`/dashboard`)
- Cards com saldo, receitas, despesas e economia do mês
- Gráfico de linha com evolução dos últimos 6 meses
- Gráfico de rosca por categorias
- Últimas 5 transações
- **IA rápida**: digite em linguagem natural e a IA registra automaticamente

### Transações (`/transacoes`)
- Listagem com filtros por tipo, categoria, mês e busca
- Adicionar, editar e excluir transações
- Totalizadores em tempo real

### IA Financeira – Chatbot (`/chatbot`)
- Perguntas em linguagem natural
- Respostas baseadas nos seus dados reais
- Sugestões de perguntas prontas
- Dicas de economia

### Relatórios (`/relatorios`)
- Relatório mensal, anual ou completo
- Gráfico de barras por categoria
- Tabela detalhada
- Exportação para CSV

---

## 4. Como Usar a IA

### Registro por linguagem natural (Dashboard)

Digite frases como:
```
gastei 45 reais com pizza
paguei 120 de gasolina
recebi 1500 de salário
comprei um livro por 60 reais
gastei 80 no cinema
```

A IA identifica automaticamente:
- **Valor** via regex
- **Tipo** (receita/despesa) por palavras-chave
- **Categoria** por dicionário de termos

### Chatbot Financeiro (`/chatbot`)

Exemplos de perguntas:
```
Quanto gastei este mês?
Qual minha maior despesa?
Quanto recebi este mês?
Qual meu saldo?
Quanto gastei com alimentação?
Me dê um resumo financeiro
Como posso economizar dinheiro?
```

---

## 5. API REST (Endpoints)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/dashboard` | Dados do dashboard |
| GET | `/api/transacoes` | Listar transações |
| POST | `/api/transacoes` | Criar transação |
| PUT | `/api/transacoes/<id>` | Editar transação |
| DELETE | `/api/transacoes/<id>` | Excluir transação |
| POST | `/api/ia/processar` | Processar linguagem natural |
| POST | `/api/chatbot` | Enviar mensagem ao chatbot |
| GET | `/api/relatorios` | Dados de relatório |
| GET | `/api/metas` | Listar metas |
| POST | `/api/metas` | Criar meta |

---

## 6. Banco de Dados

**Tabela: `transacoes`**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | Chave primária |
| descricao | TEXT | Descrição da transação |
| valor | REAL | Valor em reais |
| categoria | TEXT | Categoria (alimentacao, transporte...) |
| tipo | TEXT | "receita" ou "despesa" |
| data | TEXT | Data no formato YYYY-MM-DD |

---

## 7. Tecnologias Utilizadas

- **Backend**: Python 3 + Flask
- **Banco**: SQLite
- **Frontend**: HTML5 + CSS3 + JavaScript (Vanilla)
- **Gráficos**: Chart.js 4
- **Ícones**: Font Awesome 6
- **Fontes**: Syne + DM Sans (Google Fonts)
- **IA**: Classificação local por palavras-chave + regex

---

## 8. Personalização

Para adicionar uma nova categoria, edite em `app.py`:
1. Dicionário `KEYWORDS` — adicione palavras-chave
2. No frontend, adicione `<option>` nos selects das categorias
3. Em `style.css`, adicione a classe `.ti-novacategoria`
