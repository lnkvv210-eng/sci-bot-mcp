"""
Sci-Bot MCP Server — STDIO 版本
用于 ModelScope MCP 平台部署
"""

import os
import requests
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

# ==================== 初始化 ====================
HOST = os.environ.get("HOST", "0.0.0.0").strip().strip('"')
PORT = int(os.environ.get("PORT", os.environ.get("MCP_PORT", "8000")).strip().strip('"'))

mcp = FastMCP(
    "sci-bot",
    host=HOST,
    port=PORT,
    sse_path="/sse",
    message_path="/messages/",
    streamable_http_path="/mcp",
)

# ==================== 配置 ====================
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip().strip('"')
DEEPSEEK_BASE_URL = os.environ.get("AI_BASE_URL", "https://api.deepseek.com").strip().strip('"')
DEEPSEEK_MODEL = os.environ.get("AI_MODEL", "deepseek-chat").strip().strip('"')


def _health_payload() -> dict:
    return {
        "status": "ok",
        "name": "sci-bot",
        "transport": {
            "sse": "/sse",
            "messages": "/messages/",
            "streamable_http": "/mcp",
        },
    }


# ==================== 内部函数 ====================
def _search_papers(query: str, limit: int = 8) -> list:
    """CrossRef 论文检索"""
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": limit,
        "select": "title,author,published-print,DOI,is-referenced-by-count,abstract"
    }
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
    """DeepSeek 生成回答"""
    if not DEEPSEEK_API_KEY:
        return "⚠️ DEEPSEEK_API_KEY 未配置"

    base = DEEPSEEK_BASE_URL.rstrip('/')
    url = f"{base}/chat/completions" if base.endswith('/v1') else f"{base}/v1/chat/completions"

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "你是科研助手，基于论文回答问题，用[1][2]标注引用，用用户相同的语言回答。"},
            {"role": "user", "content": f"论文:\n{context}\n\n问题: {question}"}
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ LLM 错误: {e}"


# ==================== MCP Tools ====================
@mcp.custom_route("/", methods=["GET"], include_in_schema=False)
async def root(_request):
    return JSONResponse(_health_payload())


@mcp.custom_route("/health", methods=["GET"], include_in_schema=False)
async def health(_request):
    return JSONResponse(_health_payload())


@mcp.tool()
def search_papers(query: str, limit: int = 8) -> str:
    """Search 200M+ academic papers using CrossRef API.

    Args:
        query: Search query (e.g. "CRISPR gene editing", "transformer attention mechanism")
        limit: Number of results to return (default 8, max 20)

    Returns:
        List of papers with title, authors, year, citation count, DOI, and abstract.
    """
    limit = min(max(limit, 1), 20)
    papers = _search_papers(query, limit)

    if not papers:
        return "No papers found. Try different keywords."

    if "error" in papers[0]:
        return f"Search error: {papers[0]['error']}"

    lines = []
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p["authors"][:3])
        if len(p["authors"]) > 3:
            authors += " et al."
        lines.append(
            f"[{i}] {p['title']}\n"
            f"    Authors: {authors}\n"
            f"    Year: {p.get('year', 'N/A')} | Citations: {p['citations']}\n"
            f"    DOI: {p['doi']}\n"
            f"    URL: {p.get('url', 'N/A')}\n"
            f"    Abstract: {p.get('abstract', 'N/A')[:300]}"
        )

    return "\n\n".join(lines)


@mcp.tool()
def ask_research_question(question: str, num_references: int = 8) -> str:
    """Ask a research question and get an AI-generated answer with real paper citations.

    Searches academic papers and uses an LLM to synthesize an answer with proper citations [1][2][3].

    Args:
        question: Your research question (e.g. "What are the latest CRISPR clinical applications?")
        num_references: Number of reference papers to use (default 8, max 15)

    Returns:
        A well-structured answer with inline citations and a reference list with DOIs.
    """
    num_references = min(max(num_references, 3), 15)
    papers = _search_papers(question, num_references)

    if not papers:
        return "❌ No relevant papers found. Please try different keywords."

    if "error" in papers[0]:
        return f"❌ Search error: {papers[0]['error']}"

    # 格式化上下文
    ctx = ""
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p["authors"][:3])
        ctx += f"[{i}] {p['title']} ({p.get('year', 'N/A')}) - {authors} - DOI: {p['doi']}\n    Abstract: {p.get('abstract', '')[:300]}\n\n"

    answer = _ask_llm(question, ctx)

    # 参考文献
    refs = []
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p["authors"][:3])
        if len(p["authors"]) > 3:
            authors += " et al."
        ref = f"[{i}] {authors} ({p.get('year', 'N/A')}). {p['title']}."
        if p['doi']:
            ref += f" https://doi.org/{p['doi']}"
        refs.append(ref)

    return f"{answer}\n\n{'━' * 30}\n📚 References\n\n" + "\n".join(refs)


@mcp.tool()
def get_paper_details(doi: str) -> str:
    """Get detailed information about a specific paper by its DOI.

    Args:
        doi: The DOI of the paper (e.g. "10.1038/nature14539")

    Returns:
        Detailed paper info including full abstract, all authors, journal, and citation count.
    """
    try:
        resp = requests.get(
            f"https://api.crossref.org/works/{doi}",
            timeout=15,
            headers={"User-Agent": "SciBot-MCP/1.0"}
        )
        resp.raise_for_status()
        item = resp.json().get("message", {})

        title = (item.get("title") or ["?"])[0]
        authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in (item.get("author") or [])]
        year = (item.get("published-print") or item.get("published-online") or {}).get("date-parts", [[None]])[0][0]
        abstract = (item.get("abstract") or "无摘要").replace("<jats:p>", "").replace("</jats:p>", "")
        citations = item.get("is-referenced-by-count", 0)
        journal = (item.get("container-title") or ["N/A"])[0]

        return (
            f"📄 {title}\n\n"
            f"Authors: {', '.join(authors)}\n"
            f"Year: {year}\n"
            f"Journal: {journal}\n"
            f"Citations: {citations}\n"
            f"DOI: {doi}\n"
            f"URL: https://doi.org/{doi}\n\n"
            f"Abstract:\n{abstract}"
        )
    except requests.exceptions.HTTPError:
        return f"❌ Paper not found for DOI: {doi}"
    except Exception as e:
        return f"❌ Error: {e}"


# ==================== 启动 ====================
def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
