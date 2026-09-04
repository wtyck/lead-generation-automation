import json
from pathlib import Path


WORKFLOW_PATH = Path(__file__).parents[1] / "n8n" / "lead-intake-workflow.json"


def test_n8n_workflow_is_safe_and_importable():
    workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))

    assert workflow["active"] is False
    assert workflow["name"] == "Lead Intake - Portfolio Sample"
    assert len(workflow["nodes"]) == 4
    assert "connections" in workflow
    assert "credentials" not in json.dumps(workflow).lower()

    urls = [
        node["parameters"].get("url", "")
        for node in workflow["nodes"]
        if node["type"] == "n8n-nodes-base.httpRequest"
    ]
    assert urls == ["http://lead-api:8000/webhooks/leads"]
