import axios from 'axios'
import { fromJS, Map, OrderedMap } from 'immutable'

const SPRITE_BASE = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon'

export const spriteUrl = (id) => `${SPRITE_BASE}/${id}.png`
export const spriteUrlHd = (id) => `${SPRITE_BASE}/other/official-artwork/${id}.png`

export const TYPE_COLORS = {
    normal:   { bg: '#a8a77a', text: '#fff' },
    fire:     { bg: '#ee8130', text: '#fff' },
    water:    { bg: '#6390f0', text: '#fff' },
    electric: { bg: '#f7d02c', text: '#333' },
    grass:    { bg: '#7ac74c', text: '#fff' },
    ice:      { bg: '#96d9d6', text: '#333' },
    fighting: { bg: '#c22e28', text: '#fff' },
    poison:   { bg: '#a33ea1', text: '#fff' },
    ground:   { bg: '#e2bf65', text: '#333' },
    flying:   { bg: '#a98ff3', text: '#fff' },
    psychic:  { bg: '#f95587', text: '#fff' },
    bug:      { bg: '#a6b91a', text: '#fff' },
    rock:     { bg: '#b6a136', text: '#fff' },
    ghost:    { bg: '#735797', text: '#fff' },
    dragon:   { bg: '#6f35fc', text: '#fff' },
    dark:     { bg: '#705746', text: '#fff' },
    steel:    { bg: '#b7b7ce', text: '#333' },
    fairy:    { bg: '#d685ad', text: '#fff' },
}

export const STAT_COLORS = {
    hp:                { from: '#a8e063', to: '#56ab2f' },
    attack:            { from: '#f5af19', to: '#f12711' },
    defense:           { from: '#4facfe', to: '#00f2fe' },
    'special attack':  { from: '#a18cd1', to: '#fbc2eb' },
    'special defense': { from: '#667eea', to: '#764ba2' },
    speed:             { from: '#ffecd2', to: '#fcb69f' },
}

export const MAX_STAT = 255

export async function fetchNames() {
    try {
        const { data } = await axios.get('/api/names')
        return { names: fromJS(data.names), ids: fromJS(data.ids) }
    } catch (e) {
        console.error('Failed to fetch names:', e)
        return { names: fromJS([]), ids: Map() }
    }
}

export async function fetchCaught() {
    try {
        const { data } = await axios.get('/api/caught')
        return fromJS(data.caught)
    } catch (e) {
        console.error('Failed to fetch caught:', e)
        return Map()
    }
}

export async function fetchInfo(name) {
    try {
        const { data } = await axios.get(`/api/info/${name}`)
        return data.status ? fromJS(data.info) : null
    } catch (e) {
        console.error(`Failed to fetch info for ${name}:`, e)
        return null
    }
}

export async function fetchPokedex() {
    try {
        const { data } = await axios.get('/api/pokedex')
        return {
            entries: fromJS(data.entries),
            caught: fromJS(data.caught),
        }
    } catch (e) {
        console.error('Failed to fetch Pokédex:', e)
        return { entries: fromJS([]), caught: Map() }
    }
}

export async function fetchStats() {
    try {
        const { data } = await axios.get('/api/stats')
        return fromJS(data)
    } catch (e) {
        console.error('Failed to fetch stats:', e)
        return Map()
    }
}

export async function fetchLeaderboard(stat = 'total', limit = 10, order = 'desc') {
    try {
        const { data } = await axios.get(`/api/leaderboard?stat=${stat}&limit=${limit}&order=${order}`)
        return fromJS(data.entries)
    } catch (e) {
        console.error('Failed to fetch leaderboard:', e)
        return fromJS([])
    }
}

export async function fetchSearch(params = {}) {
    try {
        const query = new URLSearchParams(params).toString()
        const { data } = await axios.get(`/api/search?${query}`)
        return {
            results: fromJS(data.results),
            total: data.total,
        }
    } catch (e) {
        console.error('Failed to search:', e)
        return { results: fromJS([]), total: 0 }
    }
}

export async function fetchCompare(name1, name2) {
    try {
        const { data } = await axios.get(`/api/compare/${name1}/${name2}`)
        return data.status ? fromJS(data) : null
    } catch (e) {
        console.error(`Failed to compare ${name1} vs ${name2}:`, e)
        return null
    }
}

export async function catchPokemon(name) {
    try {
        const { data } = await axios.put('/api/catch', { name })
        return fromJS(data)
    } catch (e) {
        console.error(`Failed to catch ${name}:`, e)
        return fromJS({ status: false })
    }
}

export async function releasePokemon(name) {
    try {
        const { data } = await axios.put('/api/release', { name })
        return fromJS(data)
    } catch (e) {
        console.error(`Failed to release ${name}:`, e)
        return fromJS({ status: false })
    }
}

export async function fetchTypes() {
    try {
        const { data } = await axios.get('/api/types')
        return {
            types: fromJS(data.types),
            counts: fromJS(data.type_counts),
        }
    } catch (e) {
        console.error('Failed to fetch types:', e)
        return { types: fromJS([]), counts: Map() }
    }
}

export async function fetchCatchHistory(limit = 20) {
    try {
        const { data } = await axios.get(`/api/catch-history?limit=${limit}`)
        return fromJS(data.history)
    } catch (e) {
        console.error('Failed to fetch catch history:', e)
        return fromJS([])
    }
}

export function formatStatName(stat) {
    const names = {
        hp: 'HP',
        attack: 'Attack',
        defense: 'Defense',
        'special attack': 'Sp. Atk',
        'special defense': 'Sp. Def',
        'special_attack': 'Sp. Atk',
        'special_defense': 'Sp. Def',
        speed: 'Speed',
        total: 'Total',
    }
    return names[stat] || stat
}

export function typeColor(type) {
    if (!type) return TYPE_COLORS.normal
    return TYPE_COLORS[type.toLowerCase()] || TYPE_COLORS.normal
}
