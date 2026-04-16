# Ava MCP Adapter

Thin REST bridge that implements JarvisEPC's MCP tool-server contract
(`GET /tools`, `POST /execute`, `GET /health`) and proxies each tool to
the deployed `Ava_Agent` at https://ava-agent-qzmu.onrender.com, which
in turn routes to CommandDeck specialist brains.

## Why

JarvisEPC's `api/routes/mcp.ts` expects a REST tool server shape. The
existing Ava_Agent speaks FastAPI domain-specific endpoints (`/chat`,
`/projects/.../tasks`, `/broadcast`, `/v1/skills/invoke`, ...) — this
adapter is the glue that maps the REST contract onto those endpoints.

## Tools exposed

| name                 | category | upstream                                       |
| -------------------- | -------- | ---------------------------------------------- |
| `ava_chat`           | AI       | `POST /chat` → CommandDeck brain routing       |
| `ava_status`         | System   | `GET  /status`                                 |
| `ava_projects_list`  | System   | `GET  /projects`                               |
| `ava_task_submit`    | AI       | `POST /projects/{id}/tasks`                    |
| `ava_broadcast`      | AI       | `POST /broadcast`                              |
| `ava_memory_recall`  | AI       | `POST /projects/{id}/memory/recall`            |
| `ava_memory_summary` | AI       | `GET  /projects/{id}/memory`                   |
| `ava_skill_invoke`   | AI       | `POST /v1/skills/invoke`                       |
| `ava_git_status`     | System   | `GET  /projects/{id}/git/status`               |
| `ava_git_log`        | System   | `GET  /projects/{id}/git/log`                  |
| `ava_git_commit`     | System   | `POST /projects/{id}/git/commit`               |

## Deploy

Already wired to Render via `render.yaml`. Set `AVA_AGENT_API_KEY`
(copied from the `Ava_Agent` service env) in the Render dashboard.

Wire `AVA_MCP_URL=https://ava-mcp-adapter.onrender.com` into the
JarvisEPC service env; the MCP tab will switch from "Ava offline" to
showing the full merged tool catalog.
