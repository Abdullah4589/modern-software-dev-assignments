def test_create_and_list_notes(client):

    payload = {"title": "Test", "content": "Hello world"}

    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


# Write a failing tests for the search endpoint that checks for a query that does not match any notes.
def test_search_no_results(client):
    r = client.get("/notes/search/", params={"q": "Nonexistent"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 0, "Expected no results for a query that does not match any notes"


# Another failing test for the search endpoint that checks for a query that matches multiple notes.
def test_search_multiple_results(client):
    # Create multiple notes with the same content
    payload1 = {"title": "Note 1", "content": "Common content"}
    payload2 = {"title": "Note 2", "content": "Common content"}

    client.post("/notes/", json=payload1)
    client.post("/notes/", json=payload2)

    r = client.get("/notes/search/", params={"q": "Common"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 2, "Expected multiple results for a query that matches multiple notes"


def test_note_pinned_defaults_false(client):
    r = client.post("/notes/", json={"title": "A", "content": "b"})
    assert r.status_code == 201
    assert r.json()["pinned"] is False
    note_id = r.json()["id"]
    assert client.get(f"/notes/{note_id}").json()["pinned"] is False


def test_create_note_pinned(client):
    r = client.post("/notes/", json={"title": "A", "content": "b", "pinned": True})
    assert r.status_code == 201
    assert r.json()["pinned"] is True


def test_patch_note_pinned(client):
    note_id = client.post("/notes/", json={"title": "A", "content": "b"}).json()["id"]

    r = client.patch(f"/notes/{note_id}", json={"pinned": True})
    assert r.status_code == 200
    assert r.json()["pinned"] is True
    assert r.json()["title"] == "A"

    r = client.patch(f"/notes/{note_id}", json={})
    assert r.json()["pinned"] is True

    r = client.patch(f"/notes/{note_id}", json={"pinned": False})
    assert r.json()["pinned"] is False


def test_patch_note_not_found(client):
    r = client.patch("/notes/9999", json={"pinned": True})
    assert r.status_code == 404


def test_list_pinned_first(client):
    client.post("/notes/", json={"title": "first", "content": "x"})
    client.post("/notes/", json={"title": "second", "content": "x", "pinned": True})
    client.post("/notes/", json={"title": "third", "content": "x"})

    items = client.get("/notes/").json()
    assert [n["title"] for n in items] == ["second", "first", "third"]

    items = client.get("/notes/search/", params={"q": "x"}).json()
    assert items[0]["title"] == "second"


def test_delete_note(client):
    r = client.post("/notes/", json={"title": "ToDelete", "content": "bye"})
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code in (200, 204)

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404
