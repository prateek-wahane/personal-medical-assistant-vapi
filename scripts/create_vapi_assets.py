"""
Create the Vapi tools, optional custom knowledge base, and the assistant.
This script is intentionally small and readable so you can adjust it if your Vapi account uses slightly different defaults.
"""

from pathlib import Path
import json
import os

import requests


ROOT = Path(__file__).resolve().parents[1]
VAPI_BASE_URL = "https://api.vapi.ai"


def _headers():
    api_key = os.environ.get("VAPI_API_KEY")
    if not api_key:
        raise RuntimeError("Set VAPI_API_KEY before running this script.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def create_tool(tool_payload: dict, backend_url: str):
    payload = dict(tool_payload)
    payload["server"] = {"url": f"{backend_url}/api/vapi/tool-calls"}
    response = requests.post(f"{VAPI_BASE_URL}/tool", headers=_headers(), json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def create_knowledge_base(backend_url: str, secret: str):
    payload = {
        "provider": "custom-knowledge-base",
        "server": {
            "url": f"{backend_url}/api/vapi/knowledge-base",
            "secret": secret,
        },
    }
    response = requests.post(f"{VAPI_BASE_URL}/knowledge-base", headers=_headers(), json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def create_assistant(tool_ids: list[str], knowledge_base_id: str | None = None):
    prompt = (ROOT / "app" / "prompts" / "assistant_system_prompt.txt").read_text(encoding="utf-8")
    assistant_base = json.loads((ROOT / "config" / "vapi" / "assistant.json").read_text(encoding="utf-8"))

    assistant_base["model"]["messages"] = [{"role": "system", "content": prompt}]
    assistant_base["model"]["toolIds"] = tool_ids
    if knowledge_base_id:
        assistant_base["model"]["knowledgeBaseId"] = knowledge_base_id

    response = requests.post(f"{VAPI_BASE_URL}/assistant", headers=_headers(), json=assistant_base, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    backend_url = os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
    secret = os.environ.get("VAPI_WEBHOOK_SECRET", "")

    tools = json.loads((ROOT / "config" / "vapi" / "tools.json").read_text(encoding="utf-8"))
    created_tools = [create_tool(tool, backend_url) for tool in tools]
    tool_ids = [tool["id"] for tool in created_tools]

    kb = create_knowledge_base(backend_url, secret) if secret else None
    assistant = create_assistant(tool_ids, kb.get("id") if kb else None)

    output = {
        "tools": created_tools,
        "knowledge_base": kb,
        "assistant": assistant,
    }
    out_file = ROOT / "config" / "vapi" / "bootstrap_output.json"
    out_file.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
