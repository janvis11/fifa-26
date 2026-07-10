"""
Unit tests for the crowd simulation service and endpoint.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_crowd_status() -> None:
    """Verifies crowd simulation metrics and overall recommendation."""
    response = client.get("/api/crowd/metlife")
    assert response.status_code == 200
    data = response.json()
    
    assert data["stadium_id"] == "metlife"
    assert "generated_at" in data
    assert "overall_recommendation" in data
    assert len(data["zones"]) > 0
    
    for zone in data["zones"]:
        assert "zone_id" in zone
        assert "name" in zone
        assert zone["density_level"] in ("low", "medium", "high", "critical")
        assert 0 <= zone["density_pct"] <= 100
        assert "recommendation" in zone

def test_crowd_simulation_stability() -> None:
    """Ensures simulation is bucketed by minute, producing stable outcomes within same run."""
    resp1 = client.get("/api/crowd/metlife")
    resp2 = client.get("/api/crowd/metlife")
    
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    
    data1 = resp1.json()
    data2 = resp2.json()
    
    # Assert zone status counts are identical
    assert len(data1["zones"]) == len(data2["zones"])
    
    # Assert density percentages match exactly since they are minute-bucketed
    for z1, z2 in zip(data1["zones"], data2["zones"]):
        assert z1["zone_id"] == z2["zone_id"]
        assert z1["density_pct"] == z2["density_pct"]
