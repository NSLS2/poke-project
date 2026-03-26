"""
Tests for the Pokédex API status and health endpoints.
"""

import pytest


@pytest.mark.asyncio
async def test_status_returns_ok(client):
    """GET /status should return status True."""
    resp = await client.get('/status')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] is True


@pytest.mark.asyncio
async def test_status_has_timestamp(client):
    """GET /status should include an ISO timestamp."""
    resp = await client.get('/status')
    data = resp.json()
    assert 'timestamp' in data
    assert isinstance(data['timestamp'], str)
    assert len(data['timestamp']) > 10


@pytest.mark.asyncio
async def test_status_has_uptime(client):
    """GET /status should include uptime in seconds."""
    resp = await client.get('/status')
    data = resp.json()
    assert 'uptime_seconds' in data
    assert isinstance(data['uptime_seconds'], (int, float))
    assert data['uptime_seconds'] >= 0


@pytest.mark.asyncio
async def test_status_has_pokedex_size(client):
    """GET /status should include the Pokédex size."""
    resp = await client.get('/status')
    data = resp.json()
    assert 'pokedex_size' in data
    assert data['pokedex_size'] > 0


@pytest.mark.asyncio
async def test_status_has_caught_counts(client):
    """GET /status should include caught unique and total."""
    resp = await client.get('/status')
    data = resp.json()
    assert 'caught_unique' in data
    assert 'caught_total' in data
    assert isinstance(data['caught_unique'], int)
    assert isinstance(data['caught_total'], int)
