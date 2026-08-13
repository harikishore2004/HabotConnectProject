def test_search_returns_all_lsas(client, sample_lsa):
    response = client.get("/api/v1/lsas/search/")
    assert response.status_code == 200
    assert response.get_json()["count"] == 1


def test_search_by_skill(client, sample_lsa):
    response = client.get("/api/v1/lsas/search/?skills=Math")
    assert response.status_code == 200
    assert response.get_json()["count"] == 1


def test_search_by_skill_no_match(client, sample_lsa):
    response = client.get("/api/v1/lsas/search/?skills=Science")
    assert response.status_code == 200
    assert response.get_json()["count"] == 0