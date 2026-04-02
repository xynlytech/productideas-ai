"""E2E smoke test for all API endpoints."""
import httpx

BASE = "http://localhost:8000"
TOKEN = None


def auth_headers():
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def main():
    global TOKEN
    c = httpx.Client(base_url=BASE, timeout=15)

    # 1. Signup (may already exist)
    print("=== 1. SIGNUP ===")
    r = c.post("/auth/signup", json={"email": "e2e_full@test.com", "password": "TestPass123!", "name": "E2E Full"})
    if r.status_code == 201:
        print(f"  Created user: {r.json()['user']['email']}")
    else:
        print(f"  {r.json().get('detail', r.text)}")

    # 2. Login
    print("\n=== 2. LOGIN ===")
    r = c.post("/auth/login", json={"email": "e2e_full@test.com", "password": "TestPass123!"})
    assert r.status_code == 200, f"Login failed: {r.text}"
    TOKEN = r.json()["access_token"]
    print(f"  Token: {TOKEN[:20]}...")
    c.headers.update(auth_headers())

    # 3. Get me
    print("\n=== 3. GET /auth/me ===")
    r = c.get("/auth/me")
    assert r.status_code == 200
    user = r.json()
    print(f"  User: {user['email']} ({user['role']})")

    # 4. List ideas
    print("\n=== 4. LIST IDEAS ===")
    r = c.get("/ideas", params={"page": 1, "limit": 5})
    assert r.status_code == 200
    d = r.json()
    print(f"  Total: {d['total']} ideas, page {d['page']}/{d['pages']}")
    for i in d["items"][:3]:
        print(f"    [{i['score_label']}] {i['title']} (score: {i['opportunity_score']})")

    first_id = d["items"][0]["id"] if d["items"] else None

    # 5. Idea detail
    if first_id:
        print(f"\n=== 5. IDEA DETAIL (#{first_id}) ===")
        r = c.get(f"/ideas/{first_id}")
        assert r.status_code == 200
        idea = r.json()
        print(f"  Title: {idea['title']}")
        print(f"  Score: {idea['opportunity_score']} ({idea['score_label']})")
        print(f"  Demand: {idea['demand_growth_score']}, Competition: {idea['competition_score']}, Pain: {idea['pain_intensity_score']}")
        print(f"  Confidence: {idea['confidence_score']}, Momentum: {idea['momentum_score']}")
        print(f"  Cluster: {idea['cluster']['label'] if idea.get('cluster') else 'None'}")

        # 6. Related ideas
        print(f"\n=== 6. RELATED IDEAS ===")
        r = c.get(f"/ideas/{first_id}/related")
        assert r.status_code == 200
        print(f"  {len(r.json())} related ideas")

    # 7. Search & filter
    print("\n=== 7. SEARCH & FILTER ===")
    r = c.get("/ideas", params={"search": "saas", "limit": 3})
    print(f"  Search 'saas': {r.json()['total']} results")

    r = c.get("/ideas", params={"category": "E-commerce", "limit": 3})
    print(f"  Category E-commerce: {r.json()['total']} results")

    r = c.get("/ideas", params={"sort": "growth", "order": "desc", "limit": 3})
    print(f"  Sort by growth: {r.json()['total']} results")

    # 8. Clusters
    print("\n=== 8. CLUSTERS ===")
    r = c.get("/clusters")
    assert r.status_code == 200
    clusters = r.json()
    print(f"  {len(clusters)} clusters")
    if clusters:
        r = c.get(f"/clusters/{clusters[0]['id']}")
        assert r.status_code == 200
        cl = r.json()
        print(f"  Detail: {cl['label']} ({cl['idea_count']} ideas, {len(cl['keywords'])} keywords)")

    # 9. Save idea
    if first_id:
        print(f"\n=== 9. SAVE IDEA ===")
        # Delete first if exists
        r = c.get("/saved-ideas")
        for s in r.json():
            c.delete(f"/saved-ideas/{s['id']}")

        r = c.post("/saved-ideas", json={"idea_id": first_id, "note": "E2E test note"})
        assert r.status_code == 201, f"Save failed: {r.text}"
        saved = r.json()
        print(f"  Saved #{saved['id']}: {saved['idea']['title']}")
        saved_id = saved["id"]

        # 10. Update saved
        print("\n=== 10. UPDATE SAVED ===")
        r = c.patch(f"/saved-ideas/{saved_id}", json={"note": "Updated E2E note"})
        assert r.status_code == 200
        print(f"  Updated note: {r.json()['note']}")

        # 11. List saved
        print("\n=== 11. LIST SAVED ===")
        r = c.get("/saved-ideas")
        assert r.status_code == 200
        print(f"  {len(r.json())} saved ideas")

        # 12. Delete saved
        print("\n=== 12. DELETE SAVED ===")
        r = c.delete(f"/saved-ideas/{saved_id}")
        assert r.status_code == 204
        print(f"  Deleted")

    # 13. Alerts CRUD
    print("\n=== 13. CREATE ALERT ===")
    r = c.post("/alerts", json={"keyword": "automation", "min_score": 30, "cadence": "weekly"})
    assert r.status_code == 201
    alert = r.json()
    alert_id = alert["id"]
    print(f"  Alert #{alert_id}: keyword={alert['keyword']} min={alert['min_score']} active={alert['is_active']}")

    print("\n=== 14. UPDATE ALERT ===")
    r = c.patch(f"/alerts/{alert_id}", json={"is_active": False, "min_score": 50})
    assert r.status_code == 200
    print(f"  Updated: active={r.json()['is_active']} min_score={r.json()['min_score']}")

    print("\n=== 15. LIST ALERTS ===")
    r = c.get("/alerts")
    assert r.status_code == 200
    print(f"  {len(r.json())} alerts")

    print("\n=== 16. DELETE ALERT ===")
    r = c.delete(f"/alerts/{alert_id}")
    assert r.status_code == 204
    print(f"  Deleted")

    # 17. Health
    print("\n=== 17. HEALTH ===")
    r = c.get("/health")
    assert r.status_code == 200
    print(f"  {r.json()}")

    print("\n" + "=" * 50)
    print("ALL 17 E2E TESTS PASSED!")
    print("=" * 50)


if __name__ == "__main__":
    main()
