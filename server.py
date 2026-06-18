"""
Sci-Bot MCP Server — 极简 STDIO 版本
兼容 ModelScope MCP 平台
"""

import os
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sci-bot")

# ==================== 配置 ====================
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE_URL = os.environ.get("AI_BASE_URL", "https://api.deepseek.com").strip()
DEEPSEEK_MODEL = os.environ.get("AI_MODEL", "deepseek-chat").strip()


# ==================== 内部函数 ====================
def _search_papers(query: str, limit: int) -> list:
    url = "https://api.crossref.org/works"
    params = {"query": query, "rows": limit, "select": "title,author,published-print,DOI,is-referenced-by-count,abstract"}
    try:
        resp = requests.get(url, params=params, timeout=20, headers={"User-Agent": "SciBot-MCP/1.0"})
        items = resp.json().get("message", {}).get("items", [])
        papers = []
        for item in items:
            papers.append({
                "title": (item.get("title") or ["?"])[0],
                "abstract": (item.get("abstract") or "").replace("<jats:p>", "").replace("</jats:p>", ""),
                "year": (item.get("published-print") or {}).get("date-parts", [[None]])[0][0],
                "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in (item.get("author") or [])[:5]],
                "citations": item.get("is-referenced-by-count", 0),
                "doi": item.get("DOI", ""),
                "url": f"https://doi.org/{item.get('DOI', '')}" if item.get("DOI") else ""
            })
        return papers
    except Exception as e:
        return [{"error": str(e)}]


def _ask_llm(question: str, context: str) -> str:
    if not DEEPSEEK_API_KEY:
        return "DEEPSEEK_API_KEY not set"

    base = DEEPSEEK_BASE_URL.rstrip('/')
    url = f"{base}/chat/completions" if base.endswith('/v1') else f"{base}/v1/chat/completions"

    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a research assistant. Answer based on papers. Cite with [1][2]. Answer in user's language."},
                    {"role": "user", "content": f"Papers:\n{context}\n\nQuestion: {question}"}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            },
            timeout=60
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LLM error: {e}"


# ==================== MCP Tools ====================

@mcp.tool()
def search_papers(query: str, limit: int = 8) -> str:
    """Search 200M+ academic papers.

    Args:
        query: Search query (e.g. "CRISPR gene editing")
        limit: Number of results (default 8, max 20)
    """
    limit = min(max(limit, 1), 20)
    papers = _search_papers(query, limit)

    if not papers:
        return "No papers found."

    if "error" in papers[0]:
        return f"Error: {papers[0]['error']}"

    lines = []
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p["authors"][:3])
        if len(p["authors"]) > 3:
            authors += " et al."
        doi = p.get('doi', '')
        url = f"https://doi.org/{doi}" if doi else "N/A"
        lines.append(
            f"[{i}] {p['title']}\n"
            f"    {authors} ({p.get('year', 'N/A')}) | Cited: {p['citations']}\n"
            f"    DOI: {doi}\n"
            f"    URL: {url}"
        )

    return "\n\n".join(lines)


@mcp.tool()
def ask_research_question(question: str, num_references: int = 8) -> str:
    """Ask research question, get AI answer with paper citations.

    Args:
        question: Research question
        num_references: Number of references (default 8, max 15)
    """
    num_references = min(max(num_references, 3), 15)
    papers = _search_papers(question, num_references)

    if not papers or "error" in papers[0]:
        return "No papers found."

    ctx = ""
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p["authors"][:3])
        ctx += f"[{i}] {p['title']} ({p.get('year', 'N/A')}) - {authors} - DOI: {p['doi']}\n"

    answer = _ask_llm(question, ctx)

    refs = []
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p["authors"][:3])
        if len(p["authors"]) > 3:
            authors += " et al."
        doi = p.get('doi', '')
        url = f"https://doi.org/{doi}" if doi else ""
        ref = f"[{i}] {authors} ({p.get('year', 'N/A')}). {p['title']}."
        if url:
            ref += f"\n    {url}"
        refs.append(ref)

    return f"{answer}\n\n---\nReferences:\n" + "\n".join(refs)


@mcp.tool()
def get_paper_details(doi: str) -> str:
    """Get paper details by DOI.

    Args:
        doi: Paper DOI (e.g. "10.1038/nature14539")
    """
    try:
        resp = requests.get(f"https://api.crossref.org/works/{doi}", timeout=15, headers={"User-Agent": "SciBot-MCP/1.0"})
        resp.raise_for_status()
        item = resp.json().get("message", {})

        title = (item.get("title") or ["?"])[0]
        authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in (item.get("author") or [])]
        year = (item.get("published-print") or item.get("published-online") or {}).get("date-parts", [[None]])[0][0]
        abstract = (item.get("abstract") or "N/A").replace("<jats:p>", "").replace("</jats:p>", "")
        citations = item.get("is-referenced-by-count", 0)
        journal = (item.get("container-title") or ["N/A"])[0]

        return f"Title: {title}\nAuthors: {', '.join(authors)}\nYear: {year}\nJournal: {journal}\nCitations: {citations}\nDOI: {doi}\nURL: https://doi.org/{doi}\n\nAbstract:\n{abstract}"
    except Exception as e:
        return f"Error: {e}"


# ==================== 启动 ====================
def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
