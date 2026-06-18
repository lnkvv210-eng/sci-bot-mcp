# sci-bot-mcp

AI-powered research assistant MCP server for searching academic papers and answering research questions with DOI citations.

## Basic Information

- English name: sci-bot
- Chinese name: 科研论文助手
- Hosting type: Local stdio
- Category: Research, Academic Search
- Source: https://github.com/lnkvv210-eng/sci-bot-mcp

## MCP Service Configuration

```json
{
  "mcpServers": {
    "sci-bot": {
      "command": "sci-bot-mcp",
      "args": [],
      "env": {
        "DEEPSEEK_API_KEY": "your_deepseek_api_key",
        "AI_BASE_URL": "https://api.deepseek.com",
        "AI_MODEL": "deepseek-chat"
      }
    }
  }
}
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DEEPSEEK_API_KEY | Yes | - | DeepSeek API key used by `ask_research_question`. |
| AI_BASE_URL | No | https://api.deepseek.com | OpenAI-compatible API endpoint. |
| AI_MODEL | No | deepseek-chat | Chat model name. |

## Tools

### search_papers

Search academic papers through CrossRef.

- `query` (string): search query.
- `limit` (integer): number of results, default 8, max 20.

### ask_research_question

Search papers and synthesize an answer with DOI references.

- `question` (string): research question.
- `num_references` (integer): number of reference papers, default 8, max 15.

### get_paper_details

Get detailed paper metadata by DOI.

- `doi` (string): paper DOI.

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run with stdio for local MCP clients:

```bash
python server_stdio.py
```

After package installation, run the console entrypoint:

```bash
sci-bot-mcp
```
