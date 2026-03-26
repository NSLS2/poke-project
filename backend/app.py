#!/usr/bin/env python3

from asyncio import sleep as aio_sleep
from contextlib import asynccontextmanager
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from time import sleep as tm_sleep, perf_counter
from typing import Optional

from aiosqlite import connect
from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pandas import read_csv, NA
from pydantic import BaseModel
from uvicorn import run

curr_dir = Path(__file__).parent
data_dir = curr_dir / '..' / 'data'
Database = namedtuple('Database', 'game info')

STAT_COLUMNS = ['hp', 'attack', 'defense', 'special attack', 'special defense', 'speed']
SPRITE_URL = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokedex_id}.png'

@asynccontextmanager
async def lifespan(app):
    async with connect(curr_dir / 'game.etilqs') as game:
        await game.execute(dedent('''
            create table if not exists caught (
                name text primary key
              , count integer
            )
        '''))
        await game.execute(dedent('''
            create table if not exists catch_log (
                id integer primary key autoincrement
              , name text not null
              , timestamp text not null default (datetime('now'))
            )
        '''))
        await game.commit()
        yield {
            'start': perf_counter(),
            'db': Database(
                game=game,
                info=
                    read_csv(
                        data_dir / 'data.csv',
                        header=0,
                        names=['#', 'name', 'primary type', 'secondary type', 'total', 'hp', 'attack', 'defense', 'special attack', 'special defense', 'speed', 'generation', 'legendary'],
                    )
                    .rename(columns={'#': 'pokedex_id'})
                    .assign(
                        name=lambda df: df['name'].str.casefold()
                    )
                    .astype({
                        'primary type': 'category',
                        'secondary type': 'category',
                        'pokedex_id': 'Int64',
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
                        lambda df: (df['generation'] == 1)
                        & (df['name'].str.split().str.len() == 1)
                    ]
                    .set_index('name')
                    # .sort_index()
                    ,
            ),
        }

app = FastAPI(
    title='Pokédex API',
    description='A Pokédex-like API for browsing and catching Gen 1 Pokémon',
    version='0.2.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# ---------- Health / Status ----------

@app.get('/status')
async def status(request : Request):
    info = request.state.db.info
    uptime = perf_counter() - request.state.start
    async with request.state.db.game.cursor() as cur:
        await cur.execute('select count(*) from caught where count > 0')
        (caught_unique,) = await cur.fetchone()
        await cur.execute('select coalesce(sum(count), 0) from caught')
        (caught_total,) = await cur.fetchone()
    return {
        'status': True,
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': round(uptime, 2),
        'pokedex_size': len(info),
        'caught_unique': caught_unique,
        'caught_total': caught_total,
    }


# ---------- Pokédex Browsing ----------

class Monster(BaseModel):
    name : str

@app.get('/names')
async def names(request : Request):
    info = request.state.db.info
    return {
        'status': True,
        'names': [*info.index],
        'ids': info['pokedex_id'].to_dict(),
    }

@app.get('/info/{name}')
async def info(name : str, request : Request):
    try:
        row = request.state.db.info.loc[[name.casefold()]].iloc[0]
        row_dict = row.dropna().to_dict()
        pokedex_id = int(row_dict.pop('pokedex_id', 0))
        return {
            'status': True,
            'info': {
                'name': name.casefold(),
                'pokedex_id': pokedex_id,
                'sprite': SPRITE_URL.format(pokedex_id=pokedex_id),
                **row_dict,
            },
        }
    except LookupError:
        return {'status': False, 'message': f'{name} not in Pokédex.'}

@app.get('/types')
async def types(request : Request):
    info = request.state.db.info
    primary = info['primary type'].cat.categories.tolist()
    secondary = info['secondary type'].cat.categories.tolist()
    all_types = sorted(set(primary + secondary))
    type_counts = {}
    for t in all_types:
        count = int(((info['primary type'] == t) | (info['secondary type'] == t)).sum())
        type_counts[t] = count
    return {
        'status': True,
        'types': all_types,
        'type_counts': type_counts,
    }

@app.get('/search')
async def search(
    request : Request,
    q : Optional[str] = Query(None, description='Search by name (partial match)'),
    type : Optional[str] = Query(None, description='Filter by primary or secondary type'),
    legendary : Optional[bool] = Query(None, description='Filter legendary Pokémon'),
    min_total : Optional[int] = Query(None, description='Minimum total stats'),
    max_total : Optional[int] = Query(None, description='Maximum total stats'),
    sort_by : Optional[str] = Query('name', description='Sort by: name, total, hp, attack, defense, speed'),
    order : Optional[str] = Query('asc', description='Sort order: asc or desc'),
    limit : int = Query(50, ge=1, le=200, description='Max results'),
    offset : int = Query(0, ge=0, description='Offset for pagination'),
):
    info = request.state.db.info.copy()
    info = info.reset_index()

    if q:
        info = info.loc[info['name'].str.contains(q.casefold(), na=False)]

    if type:
        type_lower = type.casefold()
        info = info.loc[
            (info['primary type'].str.casefold() == type_lower)
            | (info['secondary type'].str.casefold() == type_lower)
        ]

    if legendary is not None:
        info = info.loc[info['legendary'] == legendary]

    if min_total is not None:
        info = info.loc[info['total'] >= min_total]

    if max_total is not None:
        info = info.loc[info['total'] <= max_total]

    valid_sort = {'name', 'total', 'hp', 'attack', 'defense', 'special attack', 'special defense', 'speed', 'pokedex_id'}
    if sort_by in valid_sort:
        ascending = order != 'desc'
        info = info.sort_values(sort_by, ascending=ascending)

    total = len(info)
    info = info.iloc[offset:offset + limit]

    results = []
    for _, row in info.iterrows():
        row_dict = row.dropna().to_dict()
        pid = int(row_dict.get('pokedex_id', 0))
        results.append({
            'name': row_dict.get('name', ''),
            'pokedex_id': pid,
            'sprite': SPRITE_URL.format(pokedex_id=pid),
            'primary_type': row_dict.get('primary type', ''),
            'secondary_type': row_dict.get('secondary type', ''),
            'total': int(row_dict.get('total', 0)),
            'hp': int(row_dict.get('hp', 0)),
            'attack': int(row_dict.get('attack', 0)),
            'defense': int(row_dict.get('defense', 0)),
            'special_attack': int(row_dict.get('special attack', 0)),
            'special_defense': int(row_dict.get('special defense', 0)),
            'speed': int(row_dict.get('speed', 0)),
            'legendary': bool(row_dict.get('legendary', False)),
        })

    return {
        'status': True,
        'total': total,
        'limit': limit,
        'offset': offset,
        'results': results,
    }


@app.get('/pokedex')
async def pokedex(request : Request):
    info = request.state.db.info.reset_index()
    entries = []
    for _, row in info.sort_values('pokedex_id').iterrows():
        row_dict = row.dropna().to_dict()
        pid = int(row_dict.get('pokedex_id', 0))
        entries.append({
            'name': row_dict.get('name', ''),
            'pokedex_id': pid,
            'sprite': SPRITE_URL.format(pokedex_id=pid),
            'primary_type': row_dict.get('primary type', ''),
            'secondary_type': row_dict.get('secondary type', ''),
            'total': int(row_dict.get('total', 0)),
        })

    async with request.state.db.game.cursor() as cur:
        await cur.execute('select name, count from caught where count > 0')
        caught_dict = {name: count async for name, count in cur}

    return {
        'status': True,
        'entries': entries,
        'caught': caught_dict,
    }


# ---------- Catching ----------

@app.put('/catch')
async def catch(monster : Monster, request : Request):
    name = monster.name.casefold()
    if name not in request.state.db.info.index:
        return {'status': False, 'message': f'{name} not in Pokédex.'}
    async with request.state.db.game.cursor() as cur:
        await cur.execute(dedent('''
            insert into caught (name, count) values (:name, 1)
            on conflict(name) do update set count = count + 1
        '''), {'name': name})
        await cur.execute(dedent('''
            insert into catch_log (name) values (:name)
        '''), {'name': name})
        await request.state.db.game.commit()
        await cur.execute('select count from caught where name = :name', {'name': name})
        (new_count,) = await cur.fetchone()
    return {
        'status': True,
        'name': name,
        'count': new_count,
        'message': f'Caught {name}! (×{new_count})',
    }

@app.put('/release')
async def release(monster : Monster, request : Request):
    name = monster.name.casefold()
    async with request.state.db.game.cursor() as cur:
        await cur.execute(
            'update caught set count = max(count - 1, 0) where name = :name',
            {'name': name},
        )
        await request.state.db.game.commit()
        await cur.execute('select count from caught where name = :name', {'name': name})
        row = await cur.fetchone()
        new_count = row[0] if row else 0
    return {
        'status': True,
        'name': name,
        'count': new_count,
        'message': f'Released one {name}. (×{new_count} remaining)',
    }

@app.get('/caught')
async def caught(request : Request):
    info = request.state.db.info
    async with request.state.db.game.cursor() as cur:
        await cur.execute(dedent('''
            select name, count from caught where count > 0 order by count desc
        '''))
        caught_dict = {}
        async for name, count in cur:
            pid = int(info.loc[name, 'pokedex_id']) if name in info.index else 0
            caught_dict[name] = {
                'count': count,
                'pokedex_id': pid,
                'sprite': SPRITE_URL.format(pokedex_id=pid),
            }
        return {
            'status': True,
            'caught': {name: data['count'] for name, data in caught_dict.items()},
            'details': caught_dict,
        }


# ---------- Statistics / Leaderboard ----------

@app.get('/stats')
async def stats(request : Request):
    info = request.state.db.info

    type_distribution = {}
    for t in info['primary type'].cat.categories:
        count = int((info['primary type'] == t).sum())
        if count > 0:
            type_distribution[t] = count

    stat_leaders = {}
    for stat in STAT_COLUMNS:
        top = info[stat].idxmax()
        stat_leaders[stat] = {
            'name': top,
            'value': int(info.loc[top, stat]),
            'pokedex_id': int(info.loc[top, 'pokedex_id']),
        }

    avg_stats = {stat: round(float(info[stat].mean()), 1) for stat in STAT_COLUMNS}
    avg_stats['total'] = round(float(info['total'].mean()), 1)

    return {
        'status': True,
        'total_pokemon': len(info),
        'type_distribution': type_distribution,
        'stat_leaders': stat_leaders,
        'average_stats': avg_stats,
    }

@app.get('/leaderboard')
async def leaderboard(
    request : Request,
    stat : str = Query('total', description='Stat to rank by'),
    limit : int = Query(10, ge=1, le=50),
    order : str = Query('desc', description='asc or desc'),
):
    info = request.state.db.info
    valid_stats = {'total', *STAT_COLUMNS}
    if stat not in valid_stats:
        return {'status': False, 'message': f'Invalid stat. Choose from: {", ".join(sorted(valid_stats))}'}

    ascending = order != 'desc'
    ranked = info.sort_values(stat, ascending=ascending).head(limit)

    entries = []
    for rank, (name, row) in enumerate(ranked.iterrows(), 1):
        pid = int(row['pokedex_id'])
        entries.append({
            'rank': rank,
            'name': name,
            'pokedex_id': pid,
            'sprite': SPRITE_URL.format(pokedex_id=pid),
            'value': int(row[stat]),
            'total': int(row['total']),
        })

    return {
        'status': True,
        'stat': stat,
        'order': order,
        'entries': entries,
    }

@app.get('/catch-history')
async def catch_history(
    request : Request,
    limit : int = Query(20, ge=1, le=100),
):
    async with request.state.db.game.cursor() as cur:
        await cur.execute(dedent('''
            select name, timestamp from catch_log
            order by id desc limit :limit
        '''), {'limit': limit})
        history = [
            {'name': name, 'timestamp': ts}
            async for name, ts in cur
        ]
    return {
        'status': True,
        'history': history,
    }


@app.get('/compare/{name1}/{name2}')
async def compare(name1 : str, name2 : str, request : Request):
    info = request.state.db.info
    n1, n2 = name1.casefold(), name2.casefold()
    if n1 not in info.index:
        return {'status': False, 'message': f'{name1} not in Pokédex.'}
    if n2 not in info.index:
        return {'status': False, 'message': f'{name2} not in Pokédex.'}

    row1 = info.loc[n1]
    row2 = info.loc[n2]

    def pokemon_data(name, row):
        pid = int(row['pokedex_id'])
        return {
            'name': name,
            'pokedex_id': pid,
            'sprite': SPRITE_URL.format(pokedex_id=pid),
            'stats': {stat: int(row[stat]) for stat in STAT_COLUMNS},
            'total': int(row['total']),
            'primary_type': str(row['primary type']) if row['primary type'] is not NA else None,
            'secondary_type': str(row['secondary type']) if row['secondary type'] is not NA else None,
        }

    p1 = pokemon_data(n1, row1)
    p2 = pokemon_data(n2, row2)

    comparison = {}
    for stat in STAT_COLUMNS:
        v1, v2 = p1['stats'][stat], p2['stats'][stat]
        if v1 > v2:
            winner = n1
        elif v2 > v1:
            winner = n2
        else:
            winner = 'tie'
        comparison[stat] = {
            n1: v1,
            n2: v2,
            'winner': winner,
            'difference': abs(v1 - v2),
        }

    total_wins = {n1: 0, n2: 0, 'tie': 0}
    for stat_comp in comparison.values():
        total_wins[stat_comp['winner']] += 1

    return {
        'status': True,
        'pokemon': {n1: p1, n2: p2},
        'comparison': comparison,
        'summary': {
            'stat_wins': total_wins,
            'total_winner': n1 if p1['total'] > p2['total'] else (n2 if p2['total'] > p1['total'] else 'tie'),
        },
    }


if __name__ == '__main__':
    run(app)
