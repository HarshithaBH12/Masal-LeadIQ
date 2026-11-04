from lead_manager import upsert_lead, update_lead, delete_lead

def test_upsert_replaces_same_id():
    leads = [{"id":"1","name":"Old"}]
    result = upsert_lead(leads, {"id":"1","name":"New"})
    assert len(result) == 1
    assert result[0]["name"] == "New"

def test_update_existing():
    leads = [{"id":"1","name":"A"}]
    update_lead(leads, {"id":"1","name":"B"})
    assert leads[0]["name"] == "B"

def test_delete():
    leads = [{"id":"1"},{"id":"2"}]
    assert [x["id"] for x in delete_lead(leads, "1")] == ["2"]
