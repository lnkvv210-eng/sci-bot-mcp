"""
Sci-Bot MCP Server — AI 科研助手
部署到 ModelScope MCP 平台
"""

import os
import requests
from mcp.server.fastmcp import FastMCP

# ==================== 初始化 ====================
mcp = FastMCP("Sci-Bot")

# ==================== 配置 ====================
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip().strip('"')
DEEPSEEK_BASE_URL = os.environ.get("AI_BASE_URL", "https://api.deepseek.com").strip().strip('"')
DEEPSEEK_MODEL = os.environ.get("AI_MODEL", "deepseek-chat").strip().strip('"')


# ==================== 论文检索 ====================
def _search_crossref(query: str, limit: int = 8) -> list:
    """用 CrossRef API 检索论文（2亿+索引）"""
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": limit,
        "select": "title,author,published-print,DOI,is-referenced-by-count,abstract"
    }
    try:
        resp = requests.get(
            url, params=params, timeout=20,
            headers={"User-Agent": "SciBot-MCP/1.0 (mailto:scibot@example.com)"}
        )
        resp.raise_for_status()
        items = resp.json().get("message", {}).get("items", [])

        papers = []
        for item in items:
            authors = [f"{a.get('given', '')} {a.get('family', '')}".strip()
                       for a in (item.get("author") or [])[:5]]
            papers.append({
                "title": (item.get("title") or ["未知标题"])[0],
                "abstract": (item.get("abstract") or "无摘要").replace("<jats:p>", "").replace("</jats:p>", ""),
                "year": (item.get("published-print") or {}).get("date-parts", [[None]])[0][0],
                "authors": authors,
                "citations": item.get("is-referenced-by-count", 0),
                "doi": item.get("DOI", ""),
                "url": f"https://doi.org/{item.get('DOI', '')}" if item.get("DOI") else ""
            })
        return papers
    except Exception as e:
        return [{"error": str(e)}]


def _search_semantic_scholar(query: str, limit: int = 8) -> list:
    """用 Semantic Scholar API 检索（语义搜索）"""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,year,authors,citationCount,url,openAccessPdf,externalIds"
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 429:
            return _search_crossref(query, limit)  # 降级
        resp.raise_for_status()
        data = resp.json().get("data", [])

        papers = []
        for p in data:
            pdf_url = p.get("openAccessPdf", {}).get("url", "") if p.get("openAccessPdf") else ""
            papers.append({
                "title": p.get("title", "未知标题"),
                "abstract": (p.get("abstract") or "无摘要")[:500],
                "year": p.get("year"),
                "authors": [a.get("name", "") for a in (p.get("authors") or [])[:5]],
                "citations": p.get("citationCount", 0),
                "doi": (p.get("externalIds") or {}).get("DOI", ""),
                "url": pdf_url or p.get("url", "")
            })
        return papers
    except Exception:
        return _search_crossref(query, limit)  # 降级到 CrossRef


def _format_papers_for_llm(papers: list) -> str:
    """格式化论文列表供 LLM 使用"""
    lines = []
    for i, p in enumerate(papers, 1):
        if "error" in p:
            return f"检索出错: {p['error']}"
        authors = ", ".join(p["authors"][:3])
        if len(p["authors"]) > 3:
            authors += " et al."
        lines.append(
            f"[{i}] {p['title']}\n"
            f"    Authors: {authors}\n"
            f"    Year: {p.get('year', 'N/A')} | Citations: {p['citations']}\n"
            f"    DOI: {p.get('doi', 'N/A')}\n"
            f"    URL: {p.get('url', 'N/A')}\n"
            f"    Abstract: {p.get('abstract', 'N/A')[:300]}"
        )
    return "\n\n".join(lines)


def _ask_llm(question: str, papers_context: str) -> str:
    """调用 DeepSeek 生成回答"""
    if not DEEPSEEK_API_KEY:
        return "⚠️ DEEPSEEK_API_KEY 未配置"

    base = DEEPSEEK_BASE_URL.rstrip('/')
    url = f"{base}/chat/completions" if base.endswith('/v1') else f"{base}/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional research assistant. Answer based on the provided papers.\n"
                    "Requirements:\n"
                    "1. Cite papers using [1] [2] etc.\n"
                    "2. If the papers don't contain enough info, say so honestly.\n"
                    "3. Answer in the same language as the user's question.\n"
                    "4. Be accurate, professional, and well-structured."
                )
            },
            {
                "role": "user",
                "content": f"Papers:\n{papers_context}\n\nQuestion: {question}"
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ LLM 调用出错: {e}"


# ==================== MCP Tools ====================

@mcp.tool()
def search_papers(query: str, limit: int = 8) -> str:
    """Search academic papers using Semantic Scholar (200M+ papers).

    Args:
        query: Search query (e.g. "CRISPR gene editing", "transformer attention mechanism")
        limit: Number of papers to return (default: 8, max: 20)

    Returns:
        List of papers with title, authors, year, citations, DOI, and abstract.
    """
    limit = min(max(limit, 1), 20)
    papers = _search_semantic_scholar(query, limit)

    if not papers:
        return "No papers found. Try different keywords."

    result_lines = []
    for i, p in enumerate(papers, 1):
        if "error" in p:
            return f"Search error: {p['error']}"
        authors = ", ".join(p["authors"][:3])
        if len(p["authors"]) > 3:
            authors += " et al."
        result_lines.append(
            f"[{i}] {p['title']}\n"
            f"    Authors: {authors}\n"
            f"    Year: {p.get('year', 'N/A')} | Citations: {p['citations']}\n"
            f"    DOI: {p.get('doi', 'N/A')}\n"
            f"    URL: {p.get('url', 'N/A')}\n"
            f"    Abstract: {p.get('abstract', 'N/A')[:300]}"
        )

    return "\n\n".join(result_lines)


@mcp.tool()
def ask_research_question(question: str, num_references: int = 8) -> str:
    """Ask a research question and get an AI-generated answer with real paper citations.

    This tool searches academic papers and uses an LLM to synthesize an answer
    with proper citations [1][2][3] etc.

    Args:
        question: Your research question (e.g. "What are the latest applications of CRISPR in clinical trials?")
        num_references: Number of reference papers to use (default: 8, max: 15)

    Returns:
        A well-structured answer with inline citations and a reference list.
    """
    num_references = min(max(num_references, 3), 15)

    # 1. 检索论文
    papers = _search_semantic_scholar(question, num_references)

    if not papers:
        return "❌ No relevant papers found. Please try different keywords."

    if "error" in papers[0]:
        return f"❌ Search error: {papers[0]['error']}"

    # 2. 格式化上下文
    papers_context = _format_papers_for_llm(papers)

    # 3. 生成回答
    answer = _ask_llm(question, papers_context)

    # 4. 生成参考文献列表
    refs = []
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p["authors"][:3])
        if len(p["authors"]) > 3:
            authors += " et al."
        doi = p.get("doi", "")
        ref = f"[{i}] {authors} ({p.get('year', 'N/A')}). {p['title']}."
        if doi:
            ref += f" https://doi.org/{doi}"
        refs.append(ref)

    reference_list = "\n".join(refs)

    return f"""{answer}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 References

{reference_list}
"""


@mcp.tool()
def get_paper_details(doi: str) -> str:
    """Get detailed information about a specific paper by its DOI.

    Args:
        doi: The DOI of the paper (e.g. "10.1038/nature14539")

    Returns:
        Detailed paper information including abstract, authors, and citation count.
    """
    url = f"https://api.crossref.org/works/{doi}"
    try:
        resp = requests.get(
            url, timeout=15,
            headers={"User-Agent": "SciBot-MCP/1.0 (mailto:scibot@example.com)"}
        )
        resp.raise_for_status()
        item = resp.json().get("message", {})

        title = (item.get("title") or ["未知标题"])[0]
        authors = [f"{a.get('given', '')} {a.get('family', '')}".strip()
                    for a in (item.get("author") or [])]
        year = (item.get("published-print") or item.get("published-online") or {}).get("date-parts", [[None]])[0][0]
        abstract = (item.get("abstract") or "无摘要").replace("<jats:p>", "").replace("</jats:p>", "")
        citations = item.get("is-referenced-by-count", 0)
        journal = (item.get("container-title") or ["N/A"])[0]

        return f"""📄 Paper Details

Title: {title}
Authors: {', '.join(authors)}
Year: {year}
Journal: {journal}
Citations: {citations}
DOI: {doi}
URL: https://doi.org/{doi}

Abstract:
{abstract}
"""
    except requests.exceptions.HTTPError as e:
        if "404" in str(e):
            return f"❌ Paper not found for DOI: {doi}"
        return f"❌ Error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


# ==================== 启动 ====================
if __name__ == "__main__":
    mcp.run()
