"""Test de fumée pour la Phase 1 : vérifie uniquement que l'application
démarre correctement. Aucune fonctionnalité métier n'existe encore à
tester à ce stade (voir docs/plan_de_developpement.md, Phase 1).
"""

from fastapi.testclient import TestClient

from app.main import app, settings


def test_app_metadata_matches_settings():
    assert app.title == settings.project_name
    assert app.version == settings.version


def test_app_starts_and_serves_openapi_schema():
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
