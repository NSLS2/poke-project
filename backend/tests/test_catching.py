"""
Tests for catch/release and game-related endpoints:
/catch, /release, /caught, /catch-history
"""

import pytest


# ---------- /catch ----------

@pytest.mark.asyncio
async def test_catch_known_pokemon(client, known_pokemon):
    """PUT /catch should succeed for a known Pokémon."""
    resp = await client.put('/catch', json={'name': known_pokemon})
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] is True
    assert data['name'] == known_pokemon
    assert isinstance(data['count'], int)
    assert data['count'] >= 1


@pytest.mark.asyncio
async def test_catch_returns_message(client, known_pokemon):
    """PUT /catch should return a catch message."""
    resp = await client.put('/catch', json={'name': known_pokemon})
    data = resp.json()
    assert 'message' in data
    assert known_pokemon in data['message']


@pytest.mark.asyncio
async def test_catch_increments_count(client, known_pokemon):
    """Catching the same Pokémon twice should increment the count."""
    resp1 = await client.put('/catch', json={'name': known_pokemon})
    count1 = resp1.json()['count']
    resp2 = await client.put('/catch', json={'name': known_pokemon})
    count2 = resp2.json()['count']
    assert count2 == count1 + 1


@pytest.mark.asyncio
async def test_catch_unknown_pokemon(client, unknown_pokemon):
    """PUT /catch should fail for an unknown Pokémon."""
    resp = await client.put('/catch', json={'name': unknown_pokemon})
    data = resp.json()
    assert data['status'] is False


@pytest.mark.asyncio
async def test_catch_case_insensitive(client, known_pokemon):
    """PUT /catch should be case-insensitive."""
    resp = await client.put('/catch', json={'name': known_pokemon.upper()})
    data = resp.json()
    assert data['status'] is True
    assert data['name'] == known_pokemon


# ---------- /release ----------

@pytest.mark.asyncio
async def test_release_decrements_count(client, known_pokemon):
    """PUT /release should decrement the count."""
    await client.put('/catch', json={'name': known_pokemon})
    await client.put('/catch', json={'name': known_pokemon})
    resp_before = await client.put('/catch', json={'name': known_pokemon})
    count_before = resp_before.json()['count']

    resp = await client.put('/release', json={'name': known_pokemon})
    data = resp.json()
    assert data['status'] is True
    assert data['count'] == count_before - 1


@pytest.mark.asyncio
async def test_release_does_not_go_negative(client, known_pokemon):
    """PUT /release should not let count go below 0."""
    for _ in range(100):
        await client.put('/release', json={'name': known_pokemon})
    resp = await client.put('/release', json={'name': known_pokemon})
    assert resp.json()['count'] >= 0


@pytest.mark.asyncio
async def test_release_returns_message(client, known_pokemon):
    """PUT /release should return a message."""
    await client.put('/catch', json={'name': known_pokemon})
    resp = await client.put('/release', json={'name': known_pokemon})
    data = resp.json()
    assert 'message' in data
    assert known_pokemon in data['message']


# ---------- /caught ----------

@pytest.mark.asyncio
async def test_caught_returns_dict(client):
    """GET /caught should return a caught dictionary."""
    resp = await client.get('/caught')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] is True
    assert isinstance(data['caught'], dict)


@pytest.mark.asyncio
async def test_caught_includes_details(client):
    """GET /caught should include details with sprites."""
    resp = await client.get('/caught')
    data = resp.json()
    assert 'details' in data


@pytest.mark.asyncio
async def test_caught_after_catch(client, known_pokemon):
    """A caught Pokémon should appear in GET /caught."""
    await client.put('/catch', json={'name': known_pokemon})
    resp = await client.get('/caught')
    data = resp.json()
    assert known_pokemon in data['caught']
    assert data['caught'][known_pokemon] >= 1


@pytest.mark.asyncio
async def test_caught_details_have_sprites(client, known_pokemon):
    """Caught details should include sprite URL."""
    await client.put('/catch', json={'name': known_pokemon})
    resp = await client.get('/caught')
    details = resp.json()['details']
    if known_pokemon in details:
        assert 'sprite' in details[known_pokemon]
        assert details[known_pokemon]['sprite'].startswith('https://')


@pytest.mark.asyncio
async def test_caught_excludes_zero_count(client):
    """GET /caught should not include Pokémon with count 0."""
    resp = await client.get('/caught')
    data = resp.json()
    for name, count in data['caught'].items():
        assert count > 0, f'{name} has count {count} but should be > 0'


# ---------- /catch-history ----------

@pytest.mark.asyncio
async def test_catch_history_returns_list(client):
    """GET /catch-history should return a list."""
    resp = await client.get('/catch-history')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] is True
    assert isinstance(data['history'], list)


@pytest.mark.asyncio
async def test_catch_history_has_timestamps(client, known_pokemon):
    """Catch history entries should have timestamps."""
    await client.put('/catch', json={'name': known_pokemon})
    resp = await client.get('/catch-history')
    history = resp.json()['history']
    if history:
        entry = history[0]
        assert 'name' in entry
        assert 'timestamp' in entry


@pytest.mark.asyncio
async def test_catch_history_records_catches(client, known_pokemon):
    """Catching a Pokémon should add to history."""
    await client.put('/catch', json={'name': known_pokemon})
    resp = await client.get('/catch-history')
    history = resp.json()['history']
    names = [h['name'] for h in history]
    assert known_pokemon in names


@pytest.mark.asyncio
async def test_catch_history_respects_limit(client, known_pokemon):
    """GET /catch-history?limit=N should return at most N entries."""
    for _ in range(5):
        await client.put('/catch', json={'name': known_pokemon})
    resp = await client.get('/catch-history?limit=3')
    history = resp.json()['history']
    assert len(history) <= 3


@pytest.mark.asyncio
async def test_catch_history_newest_first(client, known_pokemon):
    """History should be ordered newest first."""
    await client.put('/catch', json={'name': 'bulbasaur'})
    await client.put('/catch', json={'name': known_pokemon})
    resp = await client.get('/catch-history?limit=2')
    history = resp.json()['history']
    if len(history) >= 2:
        assert history[0]['name'] == known_pokemon
