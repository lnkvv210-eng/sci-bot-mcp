# Sci-Bot MCP Server

AI 科研助手 MCP 服务，可部署到 ModelScope MCP 平台。

## 功能

| Tool | 说明 |
|------|------|
| `search_papers` | 搜索 200M+ 学术论文 |
| `ask_research_question` | 提问并获取带引用的 AI 回答 |
| `get_paper_details` | 通过 DOI 获取论文详情 |

## 本地测试

```bash
pip install -r requirements.txt

# 设置环境变量
export DEEPSEEK_API_KEY="sk-你的key"

# 运行 MCP server
python server.py
```

## 部署到 ModelScope MCP

### 方式一：Streamable HTTP 部署

1. 将代码推送到 GitHub
2. 在 ModelScope MCP 平台创建服务
3. 填写环境变量：
   - `DEEPSEEK_API_KEY`: 你的 API key
   - `AI_BASE_URL`: `https://api.deepseek.com`
   - `AI_MODEL`: `deepseek-chat`

### 方式二：Docker 部署

```bash
docker build -t scibot-mcp .
docker run -p 8000:8000 \
  -e DEEPSEEK_API_KEY="sk-你的key" \
  scibot-mcp
```

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `DEEPSEEK_API_KEY` | ✅ | DeepSeek API Key |
| `AI_BASE_URL` | ❌ | API 地址，默认 `https://api.deepseek.com` |
| `AI_MODEL` | ❌ | 模型名，默认 `deepseek-chat` |

## MCP 客户端接入

在支持 MCP 的客户端（如 Claude Desktop、Cursor 等）中配置：

```json
{
  "mcpServers": {
    "sci-bot": {
      "url": "https://your-deployed-url/mcp"
    }
  }
}
```
