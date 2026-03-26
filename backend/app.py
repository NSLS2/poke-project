#!/usr/bin/env python3

from asyncio import sleep as aio_sleep
from contextlib import asynccontextmanager
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from time import sleep as tm_sleep, perf_counter

from aiosqlite import connect
from fastapi import FastAPI, Request, Query
from pandas import read_csv, isna, NA
from pydantic import BaseModel
from uvicorn import run

curr_dir = Path(__file__).parent
data_dir = curr_dir / '..' / 'data'
Database = namedtuple('Database', 'game info pokedex')

def _load_info():
    return (
        read_csv(
            data_dir / 'data.csv',
            header=0,
            names=['#', 'name', 'primary type', 'secondary type', 'total', 'hp', 'attack', 'defense', 'special attack', 'special defense', 'speed', 'generation', 'legendary'],
        )
        .drop('#', axis='columns')
        .assign(name=lambda df: df['name'].str.casefold())
        .astype({
            'primary type': 'category',
            'secondary type': 'category',
            'total': 'Int64',
            'hp': 'Int64',
            'attack': 'Int64',
            'defense': 'Int64',
            'special attack': 'Int64',
            'special defense': 'Int64',
            'speed': 'Int64',
            'generation': 'category',
            'legendary': 'bool',
        })
        .loc[
            lambda df: (df['generation'].astype(int) <= 4)
            & (df['name'].str.split().str.len() == 1)
        ]
        .set_index('name')
        # .sort_index()
    )

async def _build_pokedex(pokedex, info):
    await pokedex.executescript(dedent('''
        DROP TABLE IF EXISTS pokemon_fts;
        DROP TABLE IF EXISTS pokemon;
        CREATE TABLE pokemon (
            name         TEXT PRIMARY KEY,
            primary_type TEXT,
            secondary_type TEXT,
            total        INTEGER,
            hp           INTEGER,
            attack       INTEGER,
            defense      INTEGER,
            special_attack  INTEGER,
            special_defense INTEGER,
            speed        INTEGER,
            generation   INTEGER,
            legendary    INTEGER
        );
        CREATE VIRTUAL TABLE pokemon_fts
            USING fts5(name, content='pokemon', content_rowid='rowid');
    '''))
    rows = [
        (
            name,
            str(row['primary type']),
            None if isna(row['secondary type']) else str(row['secondary type']),
            int(row['total']),
            int(row['hp']),
            int(row['attack']),
            int(row['defense']),
            int(row['special attack']),
            int(row['special defense']),
            int(row['speed']),
            int(row['generation']),
            int(row['legendary']),
        )
        for name, row in info.iterrows()
    ]
    await pokedex.executemany('INSERT INTO pokemon VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', rows)
    await pokedex.execute("INSERT INTO pokemon_fts(pokemon_fts) VALUES('rebuild')")
    await pokedex.commit()

@asynccontextmanager
async def lifespan(app):
    info = _load_info()
    async with connect(curr_dir / 'game.etilqs') as game:
        await game.execute(dedent('''
            create table if not exists caught (
                name text primary key
              , count integer
            )
        '''))
        await game.commit()
        async with connect(curr_dir / 'pokedex.etilqs') as pokedex:
            await _build_pokedex(pokedex, info)
            yield {
                'start': perf_counter(),
                'db': Database(game=game, info=info, pokedex=pokedex),
            }

app = FastAPI(lifespan=lifespan)

@app.get('/status')
async def status(request : Request):
    return {'status': True, 'timestamp': datetime.now()}

class Monster(BaseModel):
    name : str

@app.get('/names')
async def names(request : Request):
    return {'status': True, 'names': [*request.state.db.info.index]}

@app.get('/info/{name}')
async def info(name : str, request : Request):
    try:
        return {
            'status': True,
            'info': {
                'name': name,
                **request.state.db.info.loc[[name.casefold()]].iloc[0].dropna().to_dict()
            },
        }
    except LookupError:
        return {'status': False, 'message': f'{name} not in Pokédex.'}

@app.put('/catch')
async def catch(monster : Monster, request : Request):
    if monster.name.casefold() not in request.state.db.info.index:
        return {'status': False}
    async with request.state.db.game.cursor() as cur:
        await cur.execute(dedent('''
            insert into caught (name, count) values (:name, 1)
            on conflict(name) do update set count = count + 1
        '''), {'name': monster.name.casefold()})
        await request.state.db.game.commit()
    return {'status': True}

@app.get('/search')
async def search(request: Request, q: str = Query(default='')):
    if not q:
        return {'status': True, 'results': []}
    async with request.state.db.pokedex.cursor() as cur:
        await cur.execute(
            "SELECT name FROM pokemon_fts WHERE name MATCH ? ORDER BY rank LIMIT 10",
            (f'{q.casefold()}*',),
        )
        results = [row[0] async for row in cur]
    return {'status': True, 'results': results}

@app.get('/caught')
async def caught(request : Request):
    async with request.state.db.game.cursor() as cur:
        await cur.execute(dedent('''
            select name, count from caught
        '''))
        return {
            'status': True,
            'caught': {
                name: count
                async for name, count in cur
                if count > 0
            },
        }

if __name__ == '__main__':
    run(app)
