import { createElement, Fragment } from '@b9g/crank'
import { spriteUrl, TYPE_COLORS, STAT_COLORS, MAX_STAT, formatStatName, typeColor } from '../api'

export function TypeBadge({ type }) {
    if (!type) return null
    const colors = typeColor(type)
    return <span
        style={`
            display: inline-flex;
            align-items: center;
            padding: 2px 10px;
            border-radius: 9999px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: ${colors.text};
            background-color: ${colors.bg};
            text-shadow: ${colors.text === '#fff' ? '0 1px 1px rgba(0,0,0,0.2)' : 'none'};
        `}
    >
        { type }
    </span>
}

export function StatBar({ label, value, maxValue, statKey }) {
    const max = maxValue || MAX_STAT
    const pct = Math.min(100, Math.round((value / max) * 100))
    const colors = STAT_COLORS[statKey] || { from: '#667eea', to: '#764ba2' }

    return <div style="display: flex; align-items: center; gap: 0.5rem; margin: 4px 0;">
        <span style="min-width: 80px; font-size: 0.8rem; font-weight: 600; color: #636e72; text-transform: capitalize;">
            { formatStatName(label) }
        </span>
        <div style="flex: 1; height: 8px; background: #dfe6e9; border-radius: 9999px; overflow: hidden;">
            <div style={`
                height: 100%;
                width: ${pct}%;
                border-radius: 9999px;
                background: linear-gradient(90deg, ${colors.from}, ${colors.to});
                transition: width 0.35s ease;
            `}></div>
        </div>
        <span style="min-width: 32px; text-align: right; font-size: 0.8rem; font-weight: 700; color: #2d3436;">
            { value }
        </span>
    </div>
}

export function StatBars({ stats }) {
    const statKeys = ['hp', 'attack', 'defense', 'special attack', 'special defense', 'speed']
    return <div style="padding: 0.5rem 0;">
        { statKeys.map(key => {
            const value = stats.get(key) || stats.get(key.replace(' ', '_'))
            if (value == null) return null
            return <StatBar
                key={key}
                label={key}
                value={value}
                statKey={key}
            />
        }) }
    </div>
}

export function SpriteImage({ id, name, size }) {
    const s = size || 48
    return <img
        src={ spriteUrl(id) }
        alt={ name || '' }
        width={ s }
        height={ s }
        style="image-rendering: pixelated; display: block;"
        loading="lazy"
    />
}

export function EmptyState({ icon, text, subtext }) {
    return <div style="text-align: center; padding: 3rem 1rem; color: #b2bec3;">
        { icon ? <div style="font-size: 3rem; margin-bottom: 0.75rem;">{ icon }</div> : null }
        <div style="font-size: 1.1rem; font-weight: 600; color: #636e72;">{ text }</div>
        { subtext ? <div style="font-size: 0.85rem; margin-top: 0.25rem;">{ subtext }</div> : null }
    </div>
}

export function Spinner({ size }) {
    const s = size || 24
    return <div style={`
        display: inline-block;
        width: ${s}px;
        height: ${s}px;
        border: 3px solid #dfe6e9;
        border-top-color: #dc0a2d;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    `}></div>
}

export function LoadingOverlay({ text }) {
    return <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 3rem; gap: 0.75rem; color: #636e72;">
        <Spinner size={ 48 } />
        <span>{ text || 'Loading...' }</span>
    </div>
}

export function Card({ children, title, badge }) {
    return <div style="
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: box-shadow 0.25s ease;
    ">
        { title ? <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid #dfe6e9;
        ">
            <h2 style="font-size: 1.5rem; font-weight: 700; color: #2d3436; margin: 0;">{ title }</h2>
            { badge != null ? <span style="
                display: inline-flex;
                align-items: center;
                padding: 0.15rem 0.5rem;
                background: #dc0a2d;
                color: white;
                border-radius: 9999px;
                font-size: 0.85rem;
                font-weight: 600;
            ">{ badge }</span> : null }
        </div> : null }
        { children }
    </div>
}

export function TabBar({ tabs, activeTab, onSelect }) {
    return <div style="
        display: flex;
        gap: 0.25rem;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #dfe6e9;
    ">
        { tabs.map(tab => <button
            key={ tab.id }
            onclick={ () => onSelect(tab.id) }
            style={`
                padding: 0.5rem 1.25rem;
                font-weight: 600;
                color: ${activeTab === tab.id ? '#dc0a2d' : '#636e72'};
                border: none;
                border-bottom: 3px solid ${activeTab === tab.id ? '#dc0a2d' : 'transparent'};
                margin-bottom: -2px;
                cursor: pointer;
                background: none;
                font-size: 0.95rem;
                transition: all 0.15s ease;
            `}
        >
            { tab.icon ? <span style="margin-right: 0.4rem;">{ tab.icon }</span> : null }
            { tab.label }
        </button>) }
    </div>
}

export function PokedexCard({ entry, isCaught, onClick }) {
    const name = entry.get('name')
    const pid = entry.get('pokedex_id')
    const primaryType = entry.get('primary_type', '')
    const colors = typeColor(primaryType)

    return <div
        onclick={ onClick }
        style={`
            background: #fff;
            border-radius: 12px;
            padding: 0.75rem;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            cursor: pointer;
            border: 2px solid ${isCaught ? '#ffcb05' : 'transparent'};
            transition: all 0.25s ease;
            position: relative;
        `}
    >
        { isCaught ? <span style="
            position: absolute;
            top: 4px;
            right: 4px;
            width: 18px;
            height: 18px;
            background: #ffcb05;
            color: #1a1a2e;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.65rem;
            font-weight: 800;
        ">✓</span> : null }
        <div style="font-size: 0.7rem; color: #b2bec3; font-weight: 600;">
            #{ String(pid).padStart(3, '0') }
        </div>
        <SpriteImage id={ pid } name={ name } size={ 64 } />
        <div style="font-size: 0.8rem; font-weight: 700; text-transform: capitalize; margin-top: 0.25rem;">
            { name }
        </div>
        <div style="display: flex; gap: 3px; justify-content: center; margin-top: 0.25rem;">
            <div style={`width: 8px; height: 8px; border-radius: 50%; background: ${colors.bg};`}></div>
        </div>
    </div>
}

export function SearchInput({ value, onInput, placeholder }) {
    return <input
        type="text"
        value={ value }
        oninput={ onInput }
        placeholder={ placeholder || 'Search Pokémon...' }
        style="
            flex: 1;
            padding: 0.5rem 1rem;
            border: 2px solid #dfe6e9;
            border-radius: 8px;
            font-size: 1rem;
            background: #fff;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
            outline: none;
        "
    />
}

export function TypeFilter({ types, selected, onSelect }) {
    return <div style="display: flex; flex-wrap: wrap; gap: 0.35rem; margin: 0.5rem 0;">
        <button
            onclick={ () => onSelect(null) }
            style={`
                padding: 4px 10px;
                border-radius: 9999px;
                font-size: 0.7rem;
                font-weight: 600;
                border: 2px solid ${!selected ? '#3b4cca' : '#dfe6e9'};
                background: ${!selected ? '#3b4cca' : '#fff'};
                color: ${!selected ? '#fff' : '#636e72'};
                cursor: pointer;
                transition: all 0.15s ease;
            `}
        >All</button>
        { types.map(t => {
            const isActive = selected === t
            const colors = typeColor(t)
            return <button
                key={ t }
                onclick={ () => onSelect(t) }
                style={`
                    padding: 4px 10px;
                    border-radius: 9999px;
                    font-size: 0.7rem;
                    font-weight: 600;
                    border: 2px solid ${isActive ? colors.bg : '#dfe6e9'};
                    background: ${isActive ? colors.bg : '#fff'};
                    color: ${isActive ? colors.text : '#636e72'};
                    cursor: pointer;
                    text-transform: capitalize;
                    transition: all 0.15s ease;
                `}
            >{ t }</button>
        }) }
    </div>
}

export function ComparisonRow({ label, val1, val2, name1, name2 }) {
    const winner = val1 > val2 ? 'left' : val2 > val1 ? 'right' : 'tie'
    return <div style="display: grid; grid-template-columns: 1fr 80px 1fr; gap: 0.5rem; align-items: center; padding: 0.35rem 0;">
        <div style={`text-align: right; font-weight: ${winner === 'left' ? '700' : '400'}; color: ${winner === 'left' ? '#dc0a2d' : '#636e72'};`}>
            { val1 }
        </div>
        <div style="text-align: center; font-size: 0.8rem; font-weight: 600; color: #b2bec3; text-transform: capitalize;">
            { formatStatName(label) }
        </div>
        <div style={`text-align: left; font-weight: ${winner === 'right' ? '700' : '400'}; color: ${winner === 'right' ? '#3b4cca' : '#636e72'};`}>
            { val2 }
        </div>
    </div>
}

export function StatsOverview({ stats }) {
    if (!stats || !stats.size) return null

    const totalPokemon = stats.get('total_pokemon', 0)
    const avgStats = stats.get('average_stats', null)
    const typeDist = stats.get('type_distribution', null)

    return <div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.75rem; margin-bottom: 1rem;">
            <div style="background: #f0f2f5; border-radius: 12px; padding: 1rem; text-align: center;">
                <div style="font-size: 2rem; font-weight: 800; color: #dc0a2d;">{ totalPokemon }</div>
                <div style="font-size: 0.8rem; color: #636e72; font-weight: 600;">Pokémon</div>
            </div>
            { avgStats ? <div style="background: #f0f2f5; border-radius: 12px; padding: 1rem; text-align: center;">
                <div style="font-size: 2rem; font-weight: 800; color: #3b4cca;">{ avgStats.get('total', 0) }</div>
                <div style="font-size: 0.8rem; color: #636e72; font-weight: 600;">Avg Total</div>
            </div> : null }
        </div>
        { typeDist ? <div>
            <h3 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.5rem;">Type Distribution</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 0.35rem;">
                { typeDist.entrySeq().sortBy(([, v]) => -v).map(([type, count]) => {
                    const colors = typeColor(type)
                    return <span
                        key={ type }
                        style={`
                            display: inline-flex;
                            align-items: center;
                            gap: 0.3rem;
                            padding: 3px 10px;
                            border-radius: 9999px;
                            font-size: 0.7rem;
                            font-weight: 600;
                            background: ${colors.bg};
                            color: ${colors.text};
                        `}
                    >
                        { type } <span style="opacity: 0.8;">({ count })</span>
                    </span>
                }) }
            </div>
        </div> : null }
    </div>
}

export function LeaderboardTable({ entries, stat }) {
    if (!entries || !entries.size) {
        return <EmptyState icon="🏆" text="No data available" />
    }
    return <table style="width: 100%; border-collapse: separate; border-spacing: 0;">
        <thead>
            <tr>
                <th style="padding: 0.5rem; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #636e72; text-align: left; border-bottom: 2px solid #dfe6e9;">#</th>
                <th style="padding: 0.5rem; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #636e72; text-align: left; border-bottom: 2px solid #dfe6e9;"></th>
                <th style="padding: 0.5rem; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #636e72; text-align: left; border-bottom: 2px solid #dfe6e9;">Name</th>
                <th style="padding: 0.5rem; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #636e72; text-align: center; border-bottom: 2px solid #dfe6e9;">{ formatStatName(stat) }</th>
            </tr>
        </thead>
        <tbody>
            { entries.map(entry => <tr key={ entry.get('name') } style="transition: background 0.15s;">
                <td style="padding: 0.4rem 0.5rem; color: #b2bec3; font-weight: 700; border-bottom: 1px solid #f0f2f5;">
                    { entry.get('rank') }
                </td>
                <td style="padding: 0.25rem; width: 40px; border-bottom: 1px solid #f0f2f5;">
                    <SpriteImage id={ entry.get('pokedex_id') } name={ entry.get('name') } size={ 36 } />
                </td>
                <td style="padding: 0.4rem 0.5rem; font-weight: 600; text-transform: capitalize; border-bottom: 1px solid #f0f2f5;">
                    { entry.get('name') }
                </td>
                <td style="padding: 0.4rem 0.5rem; text-align: center; font-weight: 700; font-size: 1.1rem; color: #dc0a2d; border-bottom: 1px solid #f0f2f5;">
                    { entry.get('value') }
                </td>
            </tr>) }
        </tbody>
    </table>
}

export function CatchHistoryList({ history }) {
    if (!history || !history.size) {
        return <EmptyState icon="📜" text="No catches yet" subtext="Go catch some Pokémon!" />
    }
    return <div>
        { history.map((entry, i) => <div
            key={ i }
            style="display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0; border-bottom: 1px solid #f0f2f5;"
        >
            <span style="font-size: 1.2rem;">⚾</span>
            <span style="font-weight: 600; text-transform: capitalize; flex: 1;">
                { entry.get('name') }
            </span>
            <span style="font-size: 0.8rem; color: #b2bec3;">
                { entry.get('timestamp', '') }
            </span>
        </div>) }
    </div>
}
