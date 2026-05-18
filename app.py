"""
FinIA - Contador Pessoal com Inteligência Artificial
Backend Flask completo com CRUD, IA local e chatbot financeiro
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import re
import json
from datetime import datetime, date
import calendar
import random

app = Flask(__name__)
DB_PATH = "database.db"

# ─────────────────────────────────────────
# BANCO DE DADOS
# ─────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Cria tabelas e insere dados de exemplo"""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT    NOT NULL,
            valor     REAL    NOT NULL,
            categoria TEXT    NOT NULL,
            tipo      TEXT    NOT NULL CHECK(tipo IN ('receita','despesa')),
            data      TEXT    NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS metas (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao  TEXT  NOT NULL,
            valor_meta REAL  NOT NULL,
            valor_atual REAL NOT NULL DEFAULT 0,
            data_limite TEXT NOT NULL
        )
    """)

    # Verificar se já há dados
    cur.execute("SELECT COUNT(*) FROM transacoes")
    count = cur.fetchone()[0]

    if count == 0:
        hoje = date.today()
        ano = hoje.year
        mes = hoje.month

        exemplos = [
            # Receitas
            ("Salário mensal",        5500.00, "salario",        "receita", f"{ano}-{mes:02d}-05"),
            ("Freelance design",       800.00, "outros",         "receita", f"{ano}-{mes:02d}-12"),
            ("Renda de investimentos", 320.00, "investimentos",  "receita", f"{ano}-{mes:02d}-01"),
            # Despesas
            ("Supermercado Pão de Açúcar", 380.00, "alimentacao", "despesa", f"{ano}-{mes:02d}-03"),
            ("iFood - Pizza",               65.00, "alimentacao", "despesa", f"{ano}-{mes:02d}-07"),
            ("Uber",                        28.50, "transporte",  "despesa", f"{ano}-{mes:02d}-09"),
            ("Gasolina",                   180.00, "transporte",  "despesa", f"{ano}-{mes:02d}-10"),
            ("Netflix",                     39.90, "lazer",       "despesa", f"{ano}-{mes:02d}-01"),
            ("Cinema",                      42.00, "lazer",       "despesa", f"{ano}-{mes:02d}-14"),
            ("Plano de saúde",             220.00, "saude",       "despesa", f"{ano}-{mes:02d}-05"),
            ("Farmácia",                    87.00, "saude",       "despesa", f"{ano}-{mes:02d}-11"),
            ("Curso Python",               150.00, "educacao",    "despesa", f"{ano}-{mes:02d}-08"),
            ("Livros",                      95.00, "educacao",    "despesa", f"{ano}-{mes:02d}-13"),
            ("Aluguel",                   1200.00, "contas",      "despesa", f"{ano}-{mes:02d}-05"),
            ("Luz",                         85.00, "contas",      "despesa", f"{ano}-{mes:02d}-10"),
            ("Internet",                    99.90, "contas",      "despesa", f"{ano}-{mes:02d}-15"),
            ("Roupa",                      240.00, "compras",     "despesa", f"{ano}-{mes:02d}-16"),
            ("Tênis",                      320.00, "compras",     "despesa", f"{ano}-{mes:02d}-18"),
        ]

        cur.executemany(
            "INSERT INTO transacoes (descricao, valor, categoria, tipo, data) VALUES (?,?,?,?,?)",
            exemplos
        )

        # Meta de exemplo
        cur.execute(
            "INSERT INTO metas (descricao, valor_meta, valor_atual, data_limite) VALUES (?,?,?,?)",
            ("Reserva de emergência", 10000.00, 3500.00, f"{ano}-12-31")
        )

    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# IA LOCAL - CLASSIFICAÇÃO AUTOMÁTICA
# ─────────────────────────────────────────

KEYWORDS = {
    "alimentacao": [
        "pizza","lanche","comida","restaurante","almoço","jantar","café","pão",
        "mercado","supermercado","ifood","rappi","delivery","sushi","hamburguer",
        "frango","carne","feira","hortifruti","açougue","padaria"
    ],
    "transporte": [
        "uber","taxi","ônibus","metrô","trem","gasolina","combustivel","estacionamento",
        "pedágio","manutenção","carro","moto","99","indriver","combustível","etanol"
    ],
    "lazer": [
        "cinema","netflix","spotify","jogos","game","show","teatro","viagem","hotel",
        "turismo","bar","balada","festa","ingresso","disney","streaming","série"
    ],
    "saude": [
        "médico","consulta","farmácia","remédio","plano","saúde","dentista","academia",
        "exame","laboratorio","cirurgia","hospital","clínica","vitamina","suplemento"
    ],
    "educacao": [
        "curso","faculdade","escola","livro","apostila","udemy","alura","coursera",
        "mensalidade","matrícula","material","caneta","caderno","certificado"
    ],
    "contas": [
        "aluguel","água","luz","energia","internet","telefone","conta","fatura",
        "iptu","condomínio","gás","tv a cabo","financiamento","parcela"
    ],
    "compras": [
        "roupa","tênis","camisa","calça","sapato","eletrônico","celular","notebook",
        "amazon","magazine","shopee","mercadolivre","presente","mochila"
    ],
    "salario": [
        "salário","salario","pagamento","renda","ordenado","vencimento","remuneração"
    ],
    "investimentos": [
        "investimento","ação","fundo","tesouro","rendimento","dividendo","cripto",
        "bitcoin","poupança","cdb","renda fixa","bolsa"
    ],
}

def classify_ai(text):
    """Classifica texto em categoria usando palavras-chave"""
    text_lower = text.lower()
    for categoria, keywords in KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return categoria
    return "outros"

def extract_value(text):
    """Extrai valor numérico do texto"""
    patterns = [
        r'r\$\s*([\d]+[.,]?[\d]*)',
        r'([\d]+[.,][\d]{2})\s*reais',
        r'([\d]+)\s*reais',
        r'([\d]+[.,][\d]*)',
        r'([\d]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            val = match.group(1).replace(',', '.')
            try:
                return float(val)
            except:
                pass
    return None

def detect_type(text):
    """Detecta se é receita ou despesa"""
    text_lower = text.lower()
    receita_words = ["recebi","ganhei","entrou","salário","salario","renda","rendimento","lucro"]
    for w in receita_words:
        if w in text_lower:
            return "receita"
    return "despesa"

def parse_natural_language(text):
    """Processa linguagem natural e retorna transação estruturada"""
    valor = extract_value(text)
    if not valor:
        return None

    tipo      = detect_type(text)
    categoria = classify_ai(text)

    # Extrair descrição (limpar números e palavras-chave de valor)
    descricao = re.sub(r'(gastei|paguei|recebi|ganhei|comprei)', '', text, flags=re.IGNORECASE)
    descricao = re.sub(r'r\$\s*[\d.,]+', '', descricao, flags=re.IGNORECASE)
    descricao = re.sub(r'[\d.,]+\s*(reais|real)', '', descricao, flags=re.IGNORECASE)
    descricao = re.sub(r'\b(de|com|no|na|em|um|uma|o|a)\b', '', descricao, flags=re.IGNORECASE)
    descricao = ' '.join(descricao.split()).strip().title()
    if not descricao:
        descricao = text.strip().title()

    return {
        "descricao": descricao[:80],
        "valor":     valor,
        "categoria": categoria,
        "tipo":      tipo,
        "data":      date.today().isoformat()
    }

# ─────────────────────────────────────────
# CHATBOT FINANCEIRO
# ─────────────────────────────────────────

def get_financial_summary():
    """Retorna resumo financeiro para o chatbot"""
    conn = get_db()
    cur  = conn.cursor()
    hoje = date.today()
    mes  = f"{hoje.year}-{hoje.month:02d}"

    cur.execute("SELECT SUM(valor) FROM transacoes WHERE tipo='receita' AND data LIKE ?", (f"{mes}%",))
    receitas = cur.fetchone()[0] or 0

    cur.execute("SELECT SUM(valor) FROM transacoes WHERE tipo='despesa' AND data LIKE ?", (f"{mes}%",))
    despesas = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT categoria, SUM(valor) as total
        FROM transacoes WHERE tipo='despesa' AND data LIKE ?
        GROUP BY categoria ORDER BY total DESC LIMIT 1
    """, (f"{mes}%",))
    maior = cur.fetchone()

    cur.execute("""
        SELECT categoria, SUM(valor) as total
        FROM transacoes WHERE tipo='despesa' AND data LIKE ?
        GROUP BY categoria ORDER BY total DESC
    """, (f"{mes}%",))
    por_cat = {r["categoria"]: r["total"] for r in cur.fetchall()}

    conn.close()
    return {
        "receitas":    receitas,
        "despesas":    despesas,
        "saldo":       receitas - despesas,
        "maior_cat":   maior["categoria"] if maior else "nenhuma",
        "maior_valor": maior["total"]     if maior else 0,
        "por_categoria": por_cat,
    }

DICAS = [
    "💡 Tente guardar pelo menos 20% da sua renda todo mês.",
    "💡 Anote cada gasto — pequenas despesas somam muito no final do mês.",
    "💡 Evite compras por impulso. Espere 24h antes de decidir.",
    "💡 Crie uma reserva de emergência equivalente a 6 meses de despesas.",
    "💡 Invista em educação financeira — é o melhor investimento.",
    "💡 Renegocie contas fixas como internet e seguro anualmente.",
    "💡 Use a regra 50/30/20: 50% necessidades, 30% desejos, 20% poupança.",
    "💡 Prefira pagar à vista para conseguir descontos.",
]

def chatbot_response(message):
    """Gera resposta inteligente do chatbot"""
    msg   = message.lower()
    dados = get_financial_summary()

    # Padrões de resposta
    if any(w in msg for w in ["gastei","despesa","gasto","saiu","paguei"]):
        if "alimenta" in msg or "comida" in msg or "food" in msg:
            val = dados["por_categoria"].get("alimentacao", 0)
            return f"🍔 Você gastou **R$ {val:.2f}** com alimentação este mês."
        if "transporte" in msg or "uber" in msg or "gasolina" in msg:
            val = dados["por_categoria"].get("transporte", 0)
            return f"🚗 Você gastou **R$ {val:.2f}** com transporte este mês."
        if "lazer" in msg or "entretenimento" in msg:
            val = dados["por_categoria"].get("lazer", 0)
            return f"🎬 Você gastou **R$ {val:.2f}** com lazer este mês."
        if "saude" in msg or "saúde" in msg:
            val = dados["por_categoria"].get("saude", 0)
            return f"❤️ Você gastou **R$ {val:.2f}** com saúde este mês."
        return f"📊 Suas despesas totais este mês são de **R$ {dados['despesas']:.2f}**."

    if any(w in msg for w in ["recebi","receita","salário","salario","ganho","entrou"]):
        return f"💰 Suas receitas totais este mês são de **R$ {dados['receitas']:.2f}**."

    if any(w in msg for w in ["saldo","sobrou","quanto tenho","economia"]):
        saldo = dados["saldo"]
        emoji = "😊" if saldo >= 0 else "😰"
        status = "positivo" if saldo >= 0 else "negativo"
        return f"{emoji} Seu saldo do mês está **{status}**: R$ {saldo:.2f}."

    if any(w in msg for w in ["maior","principal","mais gasto","top"]):
        return f"🏆 Sua maior categoria de gasto este mês é **{dados['maior_cat']}** com R$ {dados['maior_valor']:.2f}."

    if any(w in msg for w in ["dica","conselho","economizar","poupar","como"]):
        return random.choice(DICAS)

    if any(w in msg for w in ["resumo","relatório","relatorio","panorama"]):
        return (
            f"📈 **Resumo do mês:**\n"
            f"• Receitas: R$ {dados['receitas']:.2f}\n"
            f"• Despesas: R$ {dados['despesas']:.2f}\n"
            f"• Saldo: R$ {dados['saldo']:.2f}\n"
            f"• Maior gasto: {dados['maior_cat']} (R$ {dados['maior_valor']:.2f})"
        )

    if any(w in msg for w in ["olá","ola","oi","hello","hey","tudo"]):
        return "👋 Olá! Sou a **FinIA**, sua contadora inteligente. Pergunte sobre seus gastos, receitas, saldo ou peça dicas de economia!"

    if any(w in msg for w in ["obrigado","obrigada","valeu","thanks"]):
        return "😊 Por nada! Estou aqui para ajudar você a controlar melhor suas finanças!"

    # Fallback inteligente
    return (
        f"🤔 Não entendi bem, mas posso ajudar com:\n"
        f"• **Gastos do mês** — pergunte 'quanto gastei?'\n"
        f"• **Receitas** — pergunte 'quanto recebi?'\n"
        f"• **Saldo** — pergunte 'qual meu saldo?'\n"
        f"• **Dicas** — pergunte 'como economizar?'\n"
        f"• **Resumo** — pergunte 'me dê um resumo'"
    )

# ─────────────────────────────────────────
# ROTAS PRINCIPAIS
# ─────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/transacoes")
def transacoes_page():
    return render_template("transacoes.html")

@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")

@app.route("/relatorios")
def relatorios_page():
    return render_template("relatorios.html")

# ─────────────────────────────────────────
# API - TRANSAÇÕES
# ─────────────────────────────────────────

@app.route("/api/transacoes", methods=["GET"])
def api_get_transacoes():
    conn = get_db()
    cur  = conn.cursor()

    filtros = []
    params  = []

    tipo = request.args.get("tipo")
    if tipo:
        filtros.append("tipo = ?")
        params.append(tipo)

    categoria = request.args.get("categoria")
    if categoria:
        filtros.append("categoria = ?")
        params.append(categoria)

    mes = request.args.get("mes")  # formato YYYY-MM
    if mes:
        filtros.append("data LIKE ?")
        params.append(f"{mes}%")

    busca = request.args.get("busca")
    if busca:
        filtros.append("descricao LIKE ?")
        params.append(f"%{busca}%")

    where = ("WHERE " + " AND ".join(filtros)) if filtros else ""
    cur.execute(f"SELECT * FROM transacoes {where} ORDER BY data DESC, id DESC", params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/transacoes", methods=["POST"])
def api_add_transacao():
    data = request.get_json()
    required = ["descricao", "valor", "categoria", "tipo", "data"]
    for field in required:
        if field not in data or data[field] == "":
            return jsonify({"error": f"Campo '{field}' obrigatório"}), 400

    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO transacoes (descricao, valor, categoria, tipo, data) VALUES (?,?,?,?,?)",
        (data["descricao"], float(data["valor"]), data["categoria"], data["tipo"], data["data"])
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return jsonify({"success": True, "id": new_id}), 201

@app.route("/api/transacoes/<int:tid>", methods=["PUT"])
def api_update_transacao(tid):
    data = request.get_json()
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        UPDATE transacoes SET descricao=?, valor=?, categoria=?, tipo=?, data=?
        WHERE id=?
    """, (data["descricao"], float(data["valor"]), data["categoria"], data["tipo"], data["data"], tid))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/transacoes/<int:tid>", methods=["DELETE"])
def api_delete_transacao(tid):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM transacoes WHERE id=?", (tid,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# ─────────────────────────────────────────
# API - DASHBOARD
# ─────────────────────────────────────────

@app.route("/api/dashboard")
def api_dashboard():
    conn = get_db()
    cur  = conn.cursor()
    hoje = date.today()
    mes  = f"{hoje.year}-{hoje.month:02d}"

    # Totais gerais
    cur.execute("SELECT SUM(valor) FROM transacoes WHERE tipo='receita'")
    total_receitas = cur.fetchone()[0] or 0

    cur.execute("SELECT SUM(valor) FROM transacoes WHERE tipo='despesa'")
    total_despesas = cur.fetchone()[0] or 0

    # Mês atual
    cur.execute("SELECT SUM(valor) FROM transacoes WHERE tipo='receita' AND data LIKE ?", (f"{mes}%",))
    mes_receitas = cur.fetchone()[0] or 0

    cur.execute("SELECT SUM(valor) FROM transacoes WHERE tipo='despesa' AND data LIKE ?", (f"{mes}%",))
    mes_despesas = cur.fetchone()[0] or 0

    # Por categoria (mês atual)
    cur.execute("""
        SELECT categoria, SUM(valor) as total
        FROM transacoes WHERE tipo='despesa' AND data LIKE ?
        GROUP BY categoria ORDER BY total DESC
    """, (f"{mes}%",))
    por_categoria = {r["categoria"]: round(r["total"], 2) for r in cur.fetchall()}

    # Evolução dos últimos 6 meses
    evolucao = []
    for i in range(5, -1, -1):
        m = hoje.month - i
        y = hoje.year
        while m <= 0:
            m += 12
            y -= 1
        label = f"{calendar.month_abbr[m]}/{str(y)[-2:]}"
        period = f"{y}-{m:02d}"

        cur.execute("SELECT SUM(valor) FROM transacoes WHERE tipo='receita' AND data LIKE ?", (f"{period}%",))
        r = cur.fetchone()[0] or 0

        cur.execute("SELECT SUM(valor) FROM transacoes WHERE tipo='despesa' AND data LIKE ?", (f"{period}%",))
        d = cur.fetchone()[0] or 0

        evolucao.append({"mes": label, "receitas": round(r, 2), "despesas": round(d, 2)})

    # Últimas transações
    cur.execute("SELECT * FROM transacoes ORDER BY data DESC, id DESC LIMIT 5")
    ultimas = [dict(r) for r in cur.fetchall()]

    conn.close()
    return jsonify({
        "total_receitas": round(total_receitas, 2),
        "total_despesas": round(total_despesas, 2),
        "saldo":          round(total_receitas - total_despesas, 2),
        "mes_receitas":   round(mes_receitas, 2),
        "mes_despesas":   round(mes_despesas, 2),
        "mes_saldo":      round(mes_receitas - mes_despesas, 2),
        "economia_pct":   round((mes_receitas - mes_despesas) / mes_receitas * 100, 1) if mes_receitas else 0,
        "por_categoria":  por_categoria,
        "evolucao":       evolucao,
        "ultimas":        ultimas,
    })

# ─────────────────────────────────────────
# API - IA NATURAL LANGUAGE
# ─────────────────────────────────────────

@app.route("/api/ia/processar", methods=["POST"])
def api_ia_processar():
    data = request.get_json()
    texto = data.get("texto", "").strip()

    if not texto:
        return jsonify({"error": "Texto vazio"}), 400

    resultado = parse_natural_language(texto)
    if not resultado:
        return jsonify({"error": "Não foi possível identificar um valor no texto"}), 422

    # Salvar no banco
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO transacoes (descricao, valor, categoria, tipo, data) VALUES (?,?,?,?,?)",
        (resultado["descricao"], resultado["valor"], resultado["categoria"],
         resultado["tipo"], resultado["data"])
    )
    conn.commit()
    resultado["id"] = cur.lastrowid
    conn.close()

    return jsonify({"success": True, "transacao": resultado})

# ─────────────────────────────────────────
# API - CHATBOT
# ─────────────────────────────────────────

@app.route("/api/chatbot", methods=["POST"])
def api_chatbot():
    data    = request.get_json()
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Mensagem vazia"}), 400

    response = chatbot_response(message)
    return jsonify({"response": response})

# ─────────────────────────────────────────
# API - RELATÓRIOS
# ─────────────────────────────────────────

@app.route("/api/relatorios")
def api_relatorios():
    conn = get_db()
    cur  = conn.cursor()
    hoje = date.today()

    tipo_rel = request.args.get("tipo", "mensal")
    ano      = request.args.get("ano",  str(hoje.year))
    mes      = request.args.get("mes",  f"{hoje.month:02d}")

    if tipo_rel == "mensal":
        period = f"{ano}-{mes}"
        cur.execute("SELECT * FROM transacoes WHERE data LIKE ? ORDER BY data DESC", (f"{period}%",))
    elif tipo_rel == "anual":
        cur.execute("SELECT * FROM transacoes WHERE data LIKE ? ORDER BY data DESC", (f"{ano}%",))
    else:
        cur.execute("SELECT * FROM transacoes ORDER BY data DESC")

    rows = [dict(r) for r in cur.fetchall()]

    receitas = sum(r["valor"] for r in rows if r["tipo"] == "receita")
    despesas = sum(r["valor"] for r in rows if r["tipo"] == "despesa")

    por_cat = {}
    for r in rows:
        if r["tipo"] == "despesa":
            por_cat[r["categoria"]] = por_cat.get(r["categoria"], 0) + r["valor"]

    conn.close()
    return jsonify({
        "transacoes": rows,
        "totais": {
            "receitas": round(receitas, 2),
            "despesas": round(despesas, 2),
            "saldo":    round(receitas - despesas, 2),
        },
        "por_categoria": {k: round(v, 2) for k, v in sorted(por_cat.items(), key=lambda x: -x[1])},
    })

# ─────────────────────────────────────────
# API - METAS
# ─────────────────────────────────────────

@app.route("/api/metas", methods=["GET"])
def api_get_metas():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM metas ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/api/metas", methods=["POST"])
def api_add_meta():
    data = request.get_json()
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO metas (descricao, valor_meta, valor_atual, data_limite) VALUES (?,?,?,?)",
        (data["descricao"], float(data["valor_meta"]), float(data.get("valor_atual", 0)), data["data_limite"])
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True}), 201

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("  FinIA - Contador Pessoal com IA")
    print("  Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
