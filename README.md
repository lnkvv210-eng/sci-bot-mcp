# Sci-Bot MCP Server

AI-powered research assistant. Search 200M+ academic papers and get answers with real citations.

## MCP Configuration

```json
{
  "mcpServers": {
    "sci-bot": {
      "transport": "sse",
      "url": "https://your-deployed-url/sse"
    }
  }
}
```

## Tools

### search_papers
Search 200M+ academic papers using CrossRef API.

**Parameters:**
- `query` (string, required): Search query
- `limit` (integer, optional): Number of results (default: 8, max: 20)

### ask_research_question
Ask a research question and get AI-generated answer with real paper citations.

**Parameters:**
- `question` (string, required): Research question
- `num_references` (integer, optional): Number of reference papers (default: 8, max: 15)

### get_paper_details
Get detailed information about a specific paper by DOI.

**Parameters:**
- `doi` (string, required): Paper DOI (e.g. "10.1038/nature14539")

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| DEEPSEEK_API_KEY | Yes | DeepSeek API Key |
| AI_BASE_URL | No | API endpoint (default: https://api.deepseek.com) |
| AI_MODEL | No | Model name (default: deepseek-chat) |

## Local Development

```bash
pip install -r requirements.txt
export DEEPSEEK_API_KEY="sk-your-key"
python server_http.py
```

## License

MIT
