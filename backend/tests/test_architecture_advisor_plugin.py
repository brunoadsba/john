import pytest

from backend.plugins.architecture_advisor_plugin import ArchitectureAdvisorPlugin


@pytest.fixture
def plugin():
    return ArchitectureAdvisorPlugin()


def test_tool_definition(plugin):
    tool = plugin.get_tool_definition()
    assert tool["function"]["name"] == "architecture_advisor"
    actions = tool["function"]["parameters"]["properties"]["action"]["enum"]
    assert "analyze_requirements" in actions
    assert "plan_scalability" in actions


def test_analyze_requirements(plugin):
    result = plugin.execute(
        "architecture_advisor",
        {"action": "analyze_requirements", "description": "login, pagamento, latência 200ms"},
    )
    assert result["success"] is True
    assert "functional_requirements" in result["data"]


def test_security_checklist(plugin):
    result = plugin.execute(
        "architecture_advisor",
        {"action": "security_checklist", "project_type": "web", "features": ["pagamento"]},
    )
    assert result["success"] is True
    items = result["data"]["items"]
    assert any("PCI-DSS" in i for i in items)


def test_compare_solutions(plugin):
    result = plugin.execute(
        "architecture_advisor",
        {"action": "compare_solutions", "solution1": "REST", "solution2": "GraphQL", "context": {"cache_heavy": True}},
    )
    assert result["success"] is True
    assert "pros_cons" in result["data"]
    assert "REST" in result["data"]["solutions"][0].upper()


def test_plan_scalability(plugin):
    arch = {"pattern": "microservices"}
    result = plugin.execute(
        "architecture_advisor",
        {"action": "plan_scalability", "architecture": arch, "expected_users": 100000},
    )
    assert result["success"] is True
    assert "actions" in result["data"]
    assert any("API Gateway" in a for a in result["data"]["actions"])

