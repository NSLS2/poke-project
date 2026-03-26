"""
Fixtures for Pokédex API tests.
"""

import pytest
from httpx import AsyncClient, ASGITransport

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app import app


@pytest.fixture
async def client():
    """Async HTTP client for testing the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.fixture
def known_pokemon():
    """A known Gen 1 Pokémon name for testing."""
    return 'pikachu'


@pytest.fixture
def known_pokemon_id():
    """Pokédex ID for pikachu."""
    return 25


@pytest.fixture
def unknown_pokemon():
    """A name that should not exist in the Pokédex."""
    return 'fakemonster9999'


@pytest.fixture
def legendary_pokemon():
    """A known legendary Gen 1 Pokémon."""
    return 'mewtwo'


@pytest.fixture
def all_types():
    """All Gen 1 Pokémon types."""
    return [
        'bug', 'dragon', 'electric', 'fairy', 'fighting', 'fire',
        'flying', 'ghost', 'grass', 'ground', 'ice', 'normal',
        'poison', 'psychic', 'rock', 'steel', 'water',
    ]
