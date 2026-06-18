# sci-bot-mcp

AI-powered research assistant MCP server. Search 200M+ academic papers and get answers with real citations.

## Tools

- `search_papers`: Search academic papers
- `ask_research_question`: Get AI answers with citations
- `get_paper_details`: Get paper details by DOI

## Configuration

```json
{
  "command": "python",
  "args": ["server_stdio.py"],
  "env": {
    "DEEPSEEK_API_KEY": "your-api-key"
  }
}
```

## Environment Variables

- `DEEPSEEK_API_KEY` (required): DeepSeek API key
- `AI_BASE_URL` (optional): API endpoint, default `https://api.deepseek.com`
- `AI_MODEL` (optional): Model name, default `deepseek-chat`

## Install

```bash
pip install mcp requests
```

## Run

```bash
python server_stdio.py
```
