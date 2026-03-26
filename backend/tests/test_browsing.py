"""
Tests for the Pokédex browsing endpoints: /names, /info, /types, /search, /pokedex.
"""

import pytest


# ---------- /names ----------

@pytest.mark.asyncio
async def test_names_returns_list(client):
    """GET /names should return a list of Pokémon names."""
    resp = await client.get('/names')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] is True
    assert isinstance(data['names'], list)
    assert len(data['names']) > 0


@pytest.mark.asyncio
async def test_names_contains_known_pokemon(client, known_pokemon):
    """GET /names should include known Gen 1 Pokémon."""
    resp = await client.get('/names')
    data = resp.json()
    assert known_pokemon in data['names']


@pytest.mark.asyncio
async def test_names_returns_ids(client, known_pokemon, known_pokemon_id):
    """GET /names should return a name-to-id mapping."""
    resp = await client.get('/names')
    data = resp.json()
    assert 'ids' in data
    assert isinstance(data['ids'], dict)
    assert data['ids'][known_pokemon] == known_pokemon_id


@pytest.mark.asyncio
async def test_names_all_lowercase(client):
    """All names returned should be lowercase."""
    resp = await client.get('/names')
    data = resp.json()
    for name in data['names']:
        assert name == name.lower(), f'Name {name!r} is not lowercase'


# ---------- /info ----------

@pytest.mark.asyncio
async def test_info_known_pokemon(client, known_pokemon):
    """GET /info/{name} should return info for a known Pokémon."""
    resp = await client.get(f'/info/{known_pokemon}')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] is True
    info = data['info']
    assert info['name'] == known_pokemon


@pytest.mark.asyncio
async def test_info_has_stats(client, known_pokemon):
    """Pokémon info should include stats."""
    resp = await client.get(f'/info/{known_pokemon}')
    info = resp.json()['info']
    for stat in ['hp', 'attack', 'defense', 'speed', 'total']:
        assert stat in info, f'Missing stat: {stat}'
        assert isinstance(info[stat], int)


@pytest.mark.asyncio
async def test_info_has_sprite_url(client, known_pokemon, known_pokemon_id):
    """Pokémon info should include a sprite URL."""
    resp = await client.get(f'/info/{known_pokemon}')
    info = resp.json()['info']
    assert 'sprite' in info
    assert str(known_pokemon_id) in info['sprite']
    assert info['sprite'].startswith('https://')


@pytest.mark.asyncio
async def test_info_has_pokedex_id(client, known_pokemon, known_pokemon_id):
    """Pokémon info should include the Pokédex ID."""
    resp = await client.get(f'/info/{known_pokemon}')
    info = resp.json()['info']
    assert info['pokedex_id'] == known_pokemon_id


@pytest.mark.asyncio
async def test_info_has_types(client, known_pokemon):
    """Pokémon info should include primary type."""
    resp = await client.get(f'/info/{known_pokemon}')
    info = resp.json()['info']
    assert 'primary type' in info


@pytest.mark.asyncio
async def test_info_unknown_pokemon(client, unknown_pokemon):
    """GET /info/{unknown} should return status False."""
    resp = await client.get(f'/info/{unknown_pokemon}')
    data = resp.json()
    assert data['status'] is False
    assert 'message' in data


@pytest.mark.asyncio
async def test_info_case_insensitive(client, known_pokemon):
    """GET /info should be case-insensitive."""
    resp = await client.get(f'/info/{known_pokemon.upper()}')
    data = resp.json()
    assert data['status'] is True
    assert data['info']['name'] == known_pokemon


# ---------- /types ----------

@pytest.mark.asyncio
async def test_types_returns_list(client):
    """GET /types should return a list of types."""
    resp = await client.get('/types')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] is True
    assert isinstance(data['types'], list)
    assert len(data['types']) > 0


@pytest.mark.asyncio
async def test_types_includes_common_types(client):
    """GET /types should include common Gen 1 types."""
    resp = await client.get('/types')
    types = resp.json()['types']
    for t in ['Fire', 'Water', 'Grass', 'Electric', 'Normal']:
        assert t in types, f'Missing type: {t}'


@pytest.mark.asyncio
async def test_types_has_counts(client):
    """GET /types should include counts per type."""
    resp = await client.get('/types')
    data = resp.json()
    assert 'type_counts' in data
    counts = data['type_counts']
    assert isinstance(counts, dict)
    for t, count in counts.items():
        assert isinstance(count, int)
        assert count > 0


# ---------- /search ----------

@pytest.mark.asyncio
async def test_search_no_filters(client):
    """GET /search with no params returns all Pokémon."""
    resp = await client.get('/search')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] is True
    assert data['total'] > 0
    assert isinstance(data['results'], list)
    assert len(data['results']) > 0


@pytest.mark.asyncio
async def test_search_by_name(client, known_pokemon):
    """GET /search?q=pikachu should find pikachu."""
    resp = await client.get(f'/search?q={known_pokemon}')
    data = resp.json()
    assert data['total'] >= 1
    names = [r['name'] for r in data['results']]
    assert known_pokemon in names


@pytest.mark.asyncio
async def test_search_by_partial_name(client):
    """GET /search?q=char should find Charmander etc."""
    resp = await client.get('/search?q=char')
    data = resp.json()
    assert data['total'] >= 1
    for r in data['results']:
        assert 'char' in r['name']


@pytest.mark.asyncio
async def test_search_by_type(client):
    """GET /search?type=fire should return only fire types."""
    resp = await client.get('/search?type=fire')
    data = resp.json()
    assert data['total'] >= 1
    for r in data['results']:
        assert r['primary_type'].lower() == 'fire' or r.get('secondary_type', '').lower() == 'fire'


@pytest.mark.asyncio
async def test_search_by_legendary(client, legendary_pokemon):
    """GET /search?legendary=true should return legendary Pokémon."""
    resp = await client.get('/search?legendary=true')
    data = resp.json()
    assert data['total'] >= 1
    names = [r['name'] for r in data['results']]
    assert legendary_pokemon in names
    for r in data['results']:
        assert r['legendary'] is True


@pytest.mark.asyncio
async def test_search_by_stat_range(client):
    """GET /search with min/max total filters correctly."""
    resp = await client.get('/search?min_total=500&max_total=600')
    data = resp.json()
    for r in data['results']:
        assert 500 <= r['total'] <= 600


@pytest.mark.asyncio
async def test_search_sort_by_total_desc(client):
    """GET /search sorted by total descending."""
    resp = await client.get('/search?sort_by=total&order=desc&limit=10')
    data = resp.json()
    totals = [r['total'] for r in data['results']]
    assert totals == sorted(totals, reverse=True)


@pytest.mark.asyncio
async def test_search_pagination(client):
    """GET /search supports offset/limit pagination."""
    resp1 = await client.get('/search?limit=5&offset=0&sort_by=name&order=asc')
    resp2 = await client.get('/search?limit=5&offset=5&sort_by=name&order=asc')
    names1 = [r['name'] for r in resp1.json()['results']]
    names2 = [r['name'] for r in resp2.json()['results']]
    assert len(names1) == 5
    assert len(names2) == 5
    assert set(names1).isdisjoint(set(names2))


@pytest.mark.asyncio
async def test_search_result_has_sprite(client):
    """Search results should include sprite URLs."""
    resp = await client.get('/search?limit=1')
    result = resp.json()['results'][0]
    assert 'sprite' in result
    assert result['sprite'].startswith('https://')


# ---------- /pokedex ----------

@pytest.mark.asyncio
async def test_pokedex_returns_entries(client):
    """GET /pokedex should return all Pokédex entries."""
    resp = await client.get('/pokedex')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] is True
    assert isinstance(data['entries'], list)
    assert len(data['entries']) > 0


@pytest.mark.asyncio
async def test_pokedex_entry_has_required_fields(client):
    """Each Pokédex entry should have required fields."""
    resp = await client.get('/pokedex')
    entry = resp.json()['entries'][0]
    for field in ['name', 'pokedex_id', 'sprite', 'primary_type', 'total']:
        assert field in entry, f'Missing field: {field}'


@pytest.mark.asyncio
async def test_pokedex_sorted_by_id(client):
    """Pokédex entries should be sorted by Pokédex ID."""
    resp = await client.get('/pokedex')
    entries = resp.json()['entries']
    ids = [e['pokedex_id'] for e in entries]
    assert ids == sorted(ids)


@pytest.mark.asyncio
async def test_pokedex_includes_caught(client):
    """GET /pokedex should include caught dictionary."""
    resp = await client.get('/pokedex')
    data = resp.json()
    assert 'caught' in data
    assert isinstance(data['caught'], dict)
