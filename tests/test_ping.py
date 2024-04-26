async def test_ping(client):
    resp = await client.get('/ping')
    assert resp.status == 200
    assert await resp.json()["msg"] == 'pong'
