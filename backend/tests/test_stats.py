"""
Tests for stats, leaderboard, and comparison endpoints:
/stats, /leaderboard, /compare/{name1}/{name2}
"""

import pytest


# ---------- /stats ----------

@pytest.mark.asyncio
async def test_stats_returns_ok(client):
    """GET /stats should return status True."""
    resp = await client.get('/stats')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] is True


@pytest.mark.asyncio
async def test_stats_has_total_pokemon(client):
    """GET /stats should include total_pokemon count."""
    resp = await client.get('/stats')
    data = resp.json()
    assert 'total_pokemon' in data
    assert data['total_pokemon'] > 0


@pytest.mark.asyncio
async def test_stats_type_distribution(client):
    """GET /stats should include type distribution."""
    resp = await client.get('/stats')
    data = resp.json()
    assert 'type_distribution' in data
    dist = data['type_distribution']
    assert isinstance(dist, dict)
    assert len(dist) > 0
    for type_name, count in dist.items():
        assert isinstance(count, int)
        assert count > 0


@pytest.mark.asyncio
async def test_stats_stat_leaders(client):
    """GET /stats should include stat leaders."""
    resp = await client.get('/stats')
    data = resp.json()
    assert 'stat_leaders' in data
    leaders = data['stat_leaders']
    expected_stats = ['hp', 'attack', 'defense', 'special attack', 'special defense', 'speed']
    for stat in expected_stats:
        assert stat in leaders, f'Missing stat leader: {stat}'
        assert 'name' in leaders[stat]
        assert 'value' in leaders[stat]
        assert isinstance(leaders[stat]['value'], int)
        assert leaders[stat]['value'] > 0


@pytest.mark.asyncio
async def test_stats_average_stats(client):
    """GET /stats should include average stats."""
    resp = await client.get('/stats')
    data = resp.json()
    assert 'average_stats' in data
    avgs = data['average_stats']
    assert 'total' in avgs
    assert isinstance(avgs['total'], (int, float))
    for stat in ['hp', 'attack', 'defense']:
        assert stat in avgs
        assert avgs[stat] > 0


# ---------- /leaderboard ----------

@pytest.mark.asyncio
async def test_leaderboard_default(client):
    """GET /leaderboard returns top 10 by total."""
    resp = await client.get('/leaderboard')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] is True
    assert data['stat'] == 'total'
    assert isinstance(data['entries'], list)
    assert len(data['entries']) <= 10


@pytest.mark.asyncio
async def test_leaderboard_entries_have_required_fields(client):
    """Leaderboard entries should have rank, name, value, sprite."""
    resp = await client.get('/leaderboard')
    entries = resp.json()['entries']
    for entry in entries:
        assert 'rank' in entry
        assert 'name' in entry
        assert 'value' in entry
        assert 'sprite' in entry
        assert isinstance(entry['rank'], int)
        assert entry['rank'] >= 1


@pytest.mark.asyncio
async def test_leaderboard_is_sorted_desc(client):
    """Leaderboard should be sorted descending by default."""
    resp = await client.get('/leaderboard?stat=attack')
    entries = resp.json()['entries']
    values = [e['value'] for e in entries]
    assert values == sorted(values, reverse=True)


@pytest.mark.asyncio
async def test_leaderboard_sorted_asc(client):
    """Leaderboard with order=asc should be ascending."""
    resp = await client.get('/leaderboard?stat=speed&order=asc')
    entries = resp.json()['entries']
    values = [e['value'] for e in entries]
    assert values == sorted(values)


@pytest.mark.asyncio
async def test_leaderboard_custom_limit(client):
    """GET /leaderboard?limit=5 returns at most 5."""
    resp = await client.get('/leaderboard?limit=5')
    entries = resp.json()['entries']
    assert len(entries) <= 5


@pytest.mark.asyncio
async def test_leaderboard_ranks_sequential(client):
    """Ranks should be sequential starting from 1."""
    resp = await client.get('/leaderboard?limit=10')
    entries = resp.json()['entries']
    for i, entry in enumerate(entries):
        assert entry['rank'] == i + 1


@pytest.mark.asyncio
async def test_leaderboard_different_stats(client):
    """Leaderboard should work for all stat types."""
    for stat in ['hp', 'attack', 'defense', 'speed', 'total']:
        resp = await client.get(f'/leaderboard?stat={stat}')
        data = resp.json()
        assert data['status'] is True
        assert data['stat'] == stat
        assert len(data['entries']) > 0


@pytest.mark.asyncio
async def test_leaderboard_invalid_stat(client):
    """Leaderboard with invalid stat should return error."""
    resp = await client.get('/leaderboard?stat=invalid_stat')
    data = resp.json()
    assert data['status'] is False
    assert 'message' in data


# ---------- /compare ----------

@pytest.mark.asyncio
async def test_compare_two_pokemon(client, known_pokemon):
    """GET /compare/{a}/{b} should compare two Pokémon."""
    resp = await client.get(f'/compare/{known_pokemon}/charmander')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] is True


@pytest.mark.asyncio
async def test_compare_has_pokemon_data(client, known_pokemon):
    """Comparison should include data for both Pokémon."""
    resp = await client.get(f'/compare/{known_pokemon}/bulbasaur')
    data = resp.json()
    assert 'pokemon' in data
    assert known_pokemon in data['pokemon']
    assert 'bulbasaur' in data['pokemon']
    for name in [known_pokemon, 'bulbasaur']:
        p = data['pokemon'][name]
        assert 'name' in p
        assert 'sprite' in p
        assert 'stats' in p
        assert 'total' in p


@pytest.mark.asyncio
async def test_compare_has_stat_comparison(client, known_pokemon):
    """Comparison should include per-stat breakdown."""
    resp = await client.get(f'/compare/{known_pokemon}/bulbasaur')
    data = resp.json()
    assert 'comparison' in data
    comp = data['comparison']
    for stat in ['hp', 'attack', 'defense', 'speed']:
        assert stat in comp
        assert 'winner' in comp[stat]
        assert 'difference' in comp[stat]
        assert comp[stat]['difference'] >= 0


@pytest.mark.asyncio
async def test_compare_has_summary(client, known_pokemon):
    """Comparison should include a summary with stat wins."""
    resp = await client.get(f'/compare/{known_pokemon}/bulbasaur')
    data = resp.json()
    assert 'summary' in data
    summary = data['summary']
    assert 'stat_wins' in summary
    assert 'total_winner' in summary


@pytest.mark.asyncio
async def test_compare_winner_is_valid(client, known_pokemon):
    """The winner should be one of the two Pokémon or 'tie'."""
    resp = await client.get(f'/compare/{known_pokemon}/bulbasaur')
    data = resp.json()
    valid = {known_pokemon, 'bulbasaur', 'tie'}
    assert data['summary']['total_winner'] in valid
    for stat_comp in data['comparison'].values():
        assert stat_comp['winner'] in valid


@pytest.mark.asyncio
async def test_compare_unknown_first(client, unknown_pokemon, known_pokemon):
    """Comparing with unknown first Pokémon should fail."""
    resp = await client.get(f'/compare/{unknown_pokemon}/{known_pokemon}')
    data = resp.json()
    assert data['status'] is False


@pytest.mark.asyncio
async def test_compare_unknown_second(client, known_pokemon, unknown_pokemon):
    """Comparing with unknown second Pokémon should fail."""
    resp = await client.get(f'/compare/{known_pokemon}/{unknown_pokemon}')
    data = resp.json()
    assert data['status'] is False


@pytest.mark.asyncio
async def test_compare_same_pokemon(client, known_pokemon):
    """Comparing a Pokémon with itself should result in all ties."""
    resp = await client.get(f'/compare/{known_pokemon}/{known_pokemon}')
    data = resp.json()
    assert data['status'] is True
    for stat_comp in data['comparison'].values():
        assert stat_comp['winner'] == 'tie'
        assert stat_comp['difference'] == 0
    assert data['summary']['total_winner'] == 'tie'
