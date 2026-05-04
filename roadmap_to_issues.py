#!/usr/bin/env python3
"""
roadmap_to_issues.py
Lê o roadmap.md, cria GitHub Issues para cada item não concluído
e insere o link [#N](url) na linha correspondente do roadmap.

Uso:
    python roadmap_to_issues.py
    python roadmap_to_issues.py --dry-run   # mostra o que seria feito sem executar
    python roadmap_to_issues.py --sync      # fecha issues de itens marcados como [x]

Requisitos:
    - gh CLI autenticado (gh auth login)
    - Estar na raiz do repositório do projeto
"""

import subprocess
import re
import sys
import json
import argparse

ROADMAP_FILE = "docs/roadmap.md"

# ─────────────────────────────────────────
# LABELS
# ─────────────────────────────────────────

LABELS = {
    "roadmap":           ("0075ca", "Item do roadmap do projeto"),
    "em-desenvolvimento":("e4e669", "🚧 Em desenvolvimento"),
    "futuro":            ("bfd4f2", "💡 Planejado para o futuro"),
    "pre-producao":      ("d93f0b", "🚀 Obrigatório antes do deploy"),
    "em-producao":       ("0e8a16", "🏭 Configurar após o deploy"),
}

CATEGORY_LABEL_MAP = {
    "✅ Implementado":       None,
    "🚧 Em desenvolvimento": "em-desenvolvimento",
    "💡 Futuro":             "futuro",
    "🚀 Pré-produção":       "pre-producao",
    "🏭 Em produção":        "em-producao",
}


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def run_args(args: list[str]) -> tuple[str, str]:
    """Executa comando como lista de argumentos — sem shell, sem problemas de escape."""
    result = subprocess.run(args, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

def run(cmd: str) -> str:
    """Executa comando simples como string (apenas para comandos sem input do usuário)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def gh(cmd: str) -> str:
    return run(f"gh {cmd}")

def ensure_labels_exist():
    existing_raw = gh('label list --json name -q ".[].name"')
    existing = set(existing_raw.splitlines())
    for label, (color, description) in LABELS.items():
        if label not in existing:
            run_args(["gh", "label", "create", label,
                      "--color", color,
                      "--description", description])
            print(f"🏷️  Label criada: '{label}'")


# ─────────────────────────────────────────
# PARSER DO ROADMAP
# ─────────────────────────────────────────

def parse_roadmap(filepath: str) -> tuple[list[dict], list[str]]:
    items = []
    current_category = "Geral"
    current_section  = "Geral"

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        h2 = re.match(r'^##\s+(.+)', line)
        if h2:
            current_category = h2.group(1).strip()
            current_section  = current_category
            continue

        h3 = re.match(r'^###\s+(.+)', line)
        if h3:
            current_section = h3.group(1).strip()
            continue

        checkbox = re.match(r'\s*-\s+\[(x| )\]\s+(.+)', line, re.IGNORECASE)
        if checkbox:
            completed = checkbox.group(1).lower() == "x"
            raw_title = checkbox.group(2).strip()

            # Remove todos os links de issue: "[#12](url)" ou "[#0]()" em qualquer posição
            clean_title = re.sub(r'\s*\[#\d+\]\([^\)]*\)', '', raw_title).strip()
            # Remove bold/italic
            clean_title = re.sub(r'\*+', '', clean_title).strip()

            label = CATEGORY_LABEL_MAP.get(current_category)

            items.append({
                "title":     clean_title,
                "section":   current_section,
                "category":  current_category,
                "label":     label,
                "completed": completed,
                "line":      i,
            })

    return items, lines


# ─────────────────────────────────────────
# ATUALIZAÇÃO DO ROADMAP
# ─────────────────────────────────────────

def inject_issue_link(lines: list[str], line_index: int, number: int, url: str) -> list[str]:
    line = lines[line_index]
    # Remove TODOS os links de issue existentes na linha (evita duplicatas)
    line = re.sub(r'\s*\[#\d+\]\([^\)]*\)', '', line.rstrip()).rstrip()
    lines[line_index] = f"{line} [#{number}]({url})\n"
    return lines

def save_roadmap(filepath: str, lines: list[str]) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)


# ─────────────────────────────────────────
# CRIAÇÃO / FECHAMENTO DE ISSUES
# ─────────────────────────────────────────

def get_existing_issues() -> list[dict]:
    output = gh('issue list --label "roadmap" --state all --json number,title,state,url --limit 200')
    if not output:
        return []
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []

def build_issue_title(item: dict) -> str:
    return f"[{item['section']}] {item['title']}"

def create_issue(item: dict, dry_run: bool = False) -> dict | None:
    title = build_issue_title(item)
    labels = ["roadmap"]
    if item["label"]:
        labels.append(item["label"])

    body = (
        f"## Roadmap item\n\n"
        f"**Categoria:** {item['category']}  \n"
        f"**Seção:** {item['section']}  \n"
        f"**Tarefa:** {item['title']}\n\n"
        f"---\n"
        f"> Gerado automaticamente a partir do `docs/roadmap.md` (linha {item['line'] + 1}).  \n"
        f"> Quando concluído, marque o item com `[x]` e execute o comando `smart-commit`.\n"
    )

    if dry_run:
        print(f"  [DRY-RUN] Criaria: {title}")
        print(f"            Labels:  {', '.join(labels)}")
        print(f"            Roadmap: linha {item['line'] + 1} receberia [#N](url)")
        return None

    # ✅ Usa lista de argumentos — evita problemas com colchetes, \n e caracteres especiais
    cmd = ["gh", "issue", "create",
           "--title", title,
           "--body",  body]
    for label in labels:
        cmd += ["--label", label]

    stdout, stderr = run_args(cmd)

    if stderr and not stdout:
        print(f"  ❌ Erro ao criar issue: {stderr}")
        return None

    # gh retorna a URL da issue criada no stdout
    # busca em todo o output (ignora whitespace e linhas extras)
    match = re.search(r'https://github\.com/[^/]+/[^/]+/issues/(\d+)', stdout)
    if not match:
        print(f"  ❌ Não foi possível extrair número da issue.")
        print(f"     stdout: {repr(stdout)}")
        print(f"     stderr: {repr(stderr)}")
        return None

    number = int(match.group(1))
    url = match.group(0)
    print(f"  ✅ Issue criada: #{number} — {title}")
    print(f"     Labels: {', '.join(labels)}")
    print(f"     URL: {url}")
    return {"number": number, "url": url}

def close_issue(issue: dict, dry_run: bool = False) -> None:
    if dry_run:
        print(f"  [DRY-RUN] Fecharia issue #{issue['number']}: {issue['title']}")
        return
    run_args(["gh", "issue", "close", str(issue["number"]),
              "--comment", "✅ Concluído. Item marcado como [x] no roadmap.md."])
    print(f"  ✅ Issue fechada: #{issue['number']} — {issue['title']}")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sincroniza roadmap.md com GitHub Issues")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o que seria feito sem executar")
    parser.add_argument("--sync",    action="store_true", help="Fecha issues de itens já concluídos no roadmap")
    args = parser.parse_args()

    print(f"\n📋 Lendo {ROADMAP_FILE}...")

    try:
        items, lines = parse_roadmap(ROADMAP_FILE)
    except FileNotFoundError:
        print(f"❌ Arquivo {ROADMAP_FILE} não encontrado.")
        print("   Certifique-se de estar na raiz do projeto Plan N'Go.")
        sys.exit(1)

    implementados = [i for i in items if CATEGORY_LABEL_MAP.get(i["category"]) is None]
    em_dev        = [i for i in items if i["label"] == "em-desenvolvimento"]
    futuro        = [i for i in items if i["label"] == "futuro"]
    pre_prod      = [i for i in items if i["label"] == "pre-producao"]
    em_prod       = [i for i in items if i["label"] == "em-producao"]

    to_create = [i for i in items if not i["completed"] and i["label"] is not None]
    completed  = [i for i in items if     i["completed"] and i["label"] is not None]

    print(f"   {len(items)} itens no total")
    print(f"   ✅ {len(implementados)} implementados (ignorados)")
    print(f"   🚧 {len(em_dev)} em desenvolvimento")
    print(f"   💡 {len(futuro)} futuros")
    print(f"   🚀 {len(pre_prod)} pré-produção")
    print(f"   🏭 {len(em_prod)} em produção")
    print(f"   → {len(to_create)} issues a criar\n")

    ensure_labels_exist()
    existing_issues = get_existing_issues()
    existing_titles = {issue["title"] for issue in existing_issues}

    # ── Cria issues e injeta links no roadmap ──
    print("🐙 Criando issues e atualizando roadmap...")
    created = 0
    roadmap_updated = False

    for item in to_create:
        title = build_issue_title(item)

        existing = next((i for i in existing_issues if i["title"] == title), None)
        if existing:
            print(f"  ⏭️  Já existe: #{existing['number']} — {title}")
            if not args.dry_run:
                lines = inject_issue_link(lines, item["line"], existing["number"], existing["url"])
                roadmap_updated = True
            continue

        result = create_issue(item, dry_run=args.dry_run)

        if result and not args.dry_run:
            lines = inject_issue_link(lines, item["line"], result["number"], result["url"])
            roadmap_updated = True

        created += 1

    if roadmap_updated:
        save_roadmap(ROADMAP_FILE, lines)
        print(f"\n📝 roadmap.md atualizado com os links das issues")

    if created == 0 and not roadmap_updated:
        print("  Nenhuma issue nova para criar.")

    # ── Fecha issues de itens concluídos (apenas com --sync) ──
    closed = 0
    if args.sync:
        print("\n🔒 Sincronizando itens concluídos...")
        for item in completed:
            title = build_issue_title(item)
            match = next(
                (i for i in existing_issues if i["title"] == title and i["state"] == "OPEN"),
                None
            )
            if match:
                close_issue(match, dry_run=args.dry_run)
                closed += 1

        if closed == 0:
            print("  Nenhuma issue aberta para fechar.")

    # ── Resumo final ──
    print(f"\n{'='*45}")
    print(f"  Issues criadas:       {created}")
    print(f"  Roadmap atualizado:   {'sim' if roadmap_updated else 'não'}")
    if args.sync:
        print(f"  Issues fechadas:      {closed}")
    print(f"  Modo dry-run:         {'sim' if args.dry_run else 'não'}")
    print(f"{'='*45}")
    if args.dry_run:
        print("  ⚠️  Nenhuma alteração foi feita (dry-run)\n")


if __name__ == "__main__":
    main()
