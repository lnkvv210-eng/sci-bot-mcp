# sci-bot-mcp

AI research assistant MCP server. Search 200M+ papers, get answers with citations.

## MCP Configuration

```json
{
  "mcpServers": {
    "sci-bot": {
      "command": "python",
      "args": ["server.py"],
      "env": {
        "DEEPSEEK_API_KEY": "${DEEPSEEK_API_KEY}"
      }
    }
  }
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| DEEPSEEK_API_KEY | Yes | DeepSeek API Key |

## Tools

- `search_papers` - Search academic papers
- `ask_research_question` - Get AI answer with citations
- `get_paper_details` - Get paper details by DOI

## Install & Run

```bash
pip install mcp requests
export DEEPSEEK_API_KEY="your-key"
python server.py
```
