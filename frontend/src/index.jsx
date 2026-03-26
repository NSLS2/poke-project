import { renderer } from '@b9g/crank/dom'
import axios from 'axios'
import { fromJS, Map } from 'immutable'

function debounce(fn, delay) {
    let timer
    return function(...args) { clearTimeout(timer); timer = setTimeout(() => fn.apply(this, args), delay) }
}

const SPRITES = {
    pikachu:    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/25.gif',
    jigglypuff: 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/39.gif',
    clefairy:   'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/35.gif',
    eevee:      'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/133.gif',
    togepi:     'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/175.gif',
    mew:        'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/151.gif',
}

const GLOBAL_STYLE = `
    @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Press+Start+2P&display=swap');

    *, *::before, *::after { box-sizing: border-box; }

    html { scroll-behavior: smooth; }

    body {
        margin: 0;
        min-height: 100vh;
        font-family: 'Fredoka One', cursive;
        background-color: #ffb6d9;
        background-image:
            radial-gradient(circle at 20% 80%, rgba(255,182,193,0.8) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255,105,180,0.6) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(255,255,255,0.3) 0%, transparent 60%),
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60'%3E%3Ctext x='10' y='20' font-size='14' opacity='.18'%3E%E2%9C%A8%3C/text%3E%3Ctext x='35' y='45' font-size='10' opacity='.13'%3E%F0%9F%92%95%3C/text%3E%3Ctext x='5' y='50' font-size='8' opacity='.12'%3E%E2%98%85%3C/text%3E%3C/svg%3E");
        color: #a8005a;
    }

    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #ffd6e8; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #ff69b4, #ff1493);
        border-radius: 5px;
        border: 1px solid #ffb6c1;
    }

    @keyframes sparkle {
        0%,100% { opacity:1; transform:scale(1) rotate(0deg); }
        33%      { opacity:.4; transform:scale(1.4) rotate(120deg); }
        66%      { opacity:.8; transform:scale(.8) rotate(240deg); }
    }
    @keyframes float {
        0%,100% { transform:translateY(0px) rotate(-3deg); }
        50%      { transform:translateY(-14px) rotate(3deg); }
    }
    @keyframes blink {
        0%,100% { opacity:1; }
        50%      { opacity:0; }
    }
    @keyframes glitter {
        0%,100% { text-shadow: 0 0 6px #ff69b4, 0 0 12px #ff1493, 0 0 20px #ffb6c1; }
        50%      { text-shadow: 0 0 12px #ffd700, 0 0 24px #ff69b4, 0 0 36px #ff1493, 0 0 48px #fff; }
    }
    @keyframes rainbow-border {
        0%   { border-color: #ff69b4; box-shadow: 0 0 16px #ff69b4; }
        25%  { border-color: #ff1493; box-shadow: 0 0 16px #ff1493; }
        50%  { border-color: #da70d6; box-shadow: 0 0 16px #da70d6; }
        75%  { border-color: #87ceeb; box-shadow: 0 0 16px #87ceeb; }
        100% { border-color: #ff69b4; box-shadow: 0 0 16px #ff69b4; }
    }
    @keyframes pulse-glow {
        0%,100% { box-shadow: 0 4px 30px rgba(255,105,180,.35), inset 0 1px 0 rgba(255,255,255,.6); }
        50%      { box-shadow: 0 4px 50px rgba(255,20,147,.55),  inset 0 1px 0 rgba(255,255,255,.8); }
    }
    @keyframes heart-float {
        0%   { transform:translateY(0) scale(1);   opacity:1; }
        100% { transform:translateY(-80px) scale(.5); opacity:0; }
    }
    @keyframes spin-slow {
        from { transform: rotate(0deg); }
        to   { transform: rotate(360deg); }
    }
    @keyframes marquee-glow {
        0%,100% { color: #ff1493; }
        33%      { color: #9b59b6; }
        66%      { color: #3498db; }
    }

    /* ─── page shell ─── */
    #page-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0 12px 40px;
    }

    /* ─── top marquee ─── */
    .top-marquee {
        width: 100%;
        background: linear-gradient(90deg, #ff1493, #ff69b4, #da70d6, #ff69b4, #ff1493);
        color: #fff;
        font-family: 'Press Start 2P', monospace;
        font-size: 11px;
        padding: 6px 0;
        letter-spacing: 1px;
        text-shadow: 1px 1px 0 #a8005a;
        border-top: 3px double #ff1493;
        border-bottom: 3px double #ff1493;
    }

    /* ─── sprite row ─── */
    .sprite-row {
        display: flex;
        align-items: flex-end;
        gap: 4px;
        margin: 8px 0 0;
    }
    .sprite-row img {
        image-rendering: pixelated;
        filter: drop-shadow(0 2px 6px rgba(255,105,180,.7));
    }
    .sprite-row img:nth-child(odd)  { animation: float 2.4s ease-in-out infinite; }
    .sprite-row img:nth-child(even) { animation: float 2.4s ease-in-out infinite .6s; }
    .sprite-row img:nth-child(3)    { animation: float 2.4s ease-in-out infinite 1.2s; }

    /* ─── main title ─── */
    h1.site-title {
        font-family: 'Press Start 2P', monospace;
        font-size: clamp(14px, 3vw, 22px);
        text-align: center;
        color: #ff1493;
        animation: glitter 2s ease-in-out infinite;
        margin: 10px 0 4px;
        line-height: 1.7;
    }
    h1.site-title .subtitle {
        display: block;
        font-size: .5em;
        color: #c71585;
        animation: marquee-glow 3s ease-in-out infinite;
        margin-top: 4px;
    }

    /* ─── spinning star decorations ─── */
    .star-deco {
        font-size: 22px;
        display: inline-block;
        animation: spin-slow 4s linear infinite;
        filter: drop-shadow(0 0 4px #ffd700);
    }
    .star-deco.reverse { animation-direction: reverse; animation-duration: 3s; }

    /* ─── main card ─── */
    #app {
        width: 100%;
        max-width: 680px;
        background: rgba(255,240,248,0.72);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 3px solid #ff69b4;
        border-radius: 24px;
        padding: 28px 32px 32px;
        animation: pulse-glow 3s ease-in-out infinite, rainbow-border 4s linear infinite;
        margin-top: 12px;
    }

    /* ─── section headings ─── */
    h2 {
        font-family: 'Press Start 2P', monospace;
        font-size: 13px;
        color: #ff1493;
        text-align: center;
        margin: 18px 0 10px;
        text-shadow: 2px 2px 0 rgba(255,182,193,.8);
    }

    /* ─── caught listing table ─── */
    table#listing {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 4px;
        background: transparent;
    }
    table#listing thead tr th {
        background: linear-gradient(135deg, #ff69b4, #ff1493);
        color: #fff;
        font-family: 'Press Start 2P', monospace;
        font-size: 9px;
        padding: 8px 12px;
        letter-spacing: 1px;
        text-shadow: 1px 1px 0 rgba(0,0,0,.2);
        border-bottom: none;
    }
    table#listing thead tr th:first-child { border-radius: 10px 0 0 10px; }
    table#listing thead tr th:last-child  { border-radius: 0 10px 10px 0; }
    table#listing tbody tr td {
        background: rgba(255,182,193,.35);
        padding: 6px 12px;
        color: #a8005a;
        font-size: 15px;
        border-top: 1px solid rgba(255,105,180,.2);
        border-bottom: 1px solid rgba(255,105,180,.2);
        text-align: center;
    }
    table#listing tbody tr:nth-child(even) td { background: rgba(255,105,180,.18); }
    table#listing tbody tr td:first-child {
        border-radius: 10px 0 0 10px;
        border-left: 2px solid rgba(255,105,180,.4);
    }
    table#listing tbody tr td:last-child {
        border-radius: 0 10px 10px 0;
        border-right: 2px solid rgba(255,105,180,.4);
    }
    table#listing tbody tr:hover td { background: rgba(255,20,147,.15); }

    /* ─── search input ─── */
    input#search {
        width: 100%;
        padding: 10px 16px;
        border: 2px solid #ff69b4;
        border-radius: 20px;
        background: rgba(255,255,255,.75);
        color: #a8005a;
        font-family: 'Fredoka One', cursive;
        font-size: 17px;
        outline: none;
        transition: border-color .2s, box-shadow .2s;
        box-shadow: 0 2px 10px rgba(255,105,180,.25), inset 0 1px 0 rgba(255,255,255,.8);
        margin-bottom: 8px;
    }
    input#search::placeholder { color: #ffb6c1; }
    input#search:focus {
        border-color: #ff1493;
        box-shadow: 0 0 0 3px rgba(255,20,147,.2), 0 2px 10px rgba(255,105,180,.35);
    }

    /* ─── dropdown ─── */
    select#catcher {
        width: 100%;
        padding: 10px 16px;
        border: 2px solid #ff69b4;
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(255,240,248,.9), rgba(255,182,193,.6));
        color: #a8005a;
        font-family: 'Fredoka One', cursive;
        font-size: 16px;
        outline: none;
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(255,105,180,.2), inset 0 1px 0 rgba(255,255,255,.7);
        margin-bottom: 10px;
        transition: border-color .2s;
        -webkit-appearance: none;
        appearance: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20'%3E%3Ctext y='16' font-size='16'%3E%F0%9F%92%95%3C/text%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 12px center;
        padding-right: 40px;
    }
    select#catcher:focus { border-color: #ff1493; }

    /* ─── catch button ─── */
    button#catcher {
        width: 100%;
        padding: 12px;
        background: linear-gradient(135deg, #ff69b4 0%, #ff1493 50%, #c71585 100%);
        color: #fff;
        border: none;
        border-radius: 20px;
        font-family: 'Press Start 2P', monospace;
        font-size: 12px;
        letter-spacing: 1px;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(255,20,147,.5), 0 2px 0 #a8005a, inset 0 1px 0 rgba(255,255,255,.4);
        transition: transform .1s, box-shadow .1s;
        text-shadow: 1px 1px 0 rgba(0,0,0,.2);
        margin-top: 4px;
    }
    button#catcher:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255,20,147,.6), 0 2px 0 #a8005a, inset 0 1px 0 rgba(255,255,255,.4);
    }
    button#catcher:active { transform: translateY(1px); box-shadow: 0 2px 8px rgba(255,20,147,.4), inset 0 1px 0 rgba(255,255,255,.3); }

    /* ─── info box ─── */
    dl#info-box {
        display: grid;
        grid-template-columns: 40% 1fr;
        gap: 3px 0;
        background: rgba(255,240,248,.7);
        border: 2px dashed #ff69b4;
        border-radius: 16px;
        padding: 14px 18px;
        margin: 10px 0;
        min-width: unset;
        width: 100%;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.6);
    }
    dl#info-box dt {
        font-weight: bold;
        color: #ff1493;
        font-size: 14px;
        grid-column: 1;
        padding: 2px 0;
    }
    dl#info-box dd {
        color: #a8005a;
        font-size: 14px;
        grid-column: 2;
        margin: 0;
        padding: 2px 0;
    }

    /* ─── footer ─── */
    .page-footer {
        margin-top: 18px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        font-size: 11px;
        color: #ff69b4;
    }
    .footer-buttons {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
        justify-content: center;
    }
    .btn-88x31 {
        display: inline-block;
        width: 88px;
        height: 31px;
        background: linear-gradient(135deg, #ff69b4, #ff1493);
        border: 1px solid #c71585;
        border-radius: 4px;
        color: #fff;
        font-family: 'Press Start 2P', monospace;
        font-size: 6px;
        text-align: center;
        line-height: 31px;
        box-shadow: 1px 1px 0 rgba(0,0,0,.2);
        animation: sparkle 2s ease-in-out infinite;
        cursor: default;
        letter-spacing: .5px;
    }
    .btn-88x31:nth-child(2) { animation-delay: .5s; background: linear-gradient(135deg, #da70d6, #9b59b6); border-color: #7d3c98; }
    .btn-88x31:nth-child(3) { animation-delay: 1s;  background: linear-gradient(135deg, #87ceeb, #5dade2); border-color: #2e86c1; }
    .visitor-counter {
        font-family: 'Press Start 2P', monospace;
        font-size: 9px;
        color: #c71585;
        background: rgba(255,240,248,.8);
        border: 2px solid #ff69b4;
        border-radius: 8px;
        padding: 4px 10px;
        animation: blink 2s step-end infinite;
    }
    .footer-marquee {
        width: 100%;
        max-width: 680px;
        font-size: 11px;
        color: #c71585;
        animation: marquee-glow 3s ease-in-out infinite;
    }
`

function Listing({ monsters }) {
    const rows = do {
        monsters.entrySeq().map(([k, v]) => <tr>
            <td>✨ { k }</td>
            <td>💕 { v }</td>
        </tr>)
    }
    return <>
        <h2>💖 Current Pokémon 💖</h2>
        <table id="listing">
            <thead>
                <tr>
                    <th>★ Name ★</th>
                    <th>★ Count ★</th>
                </tr>
            </thead>
            <tbody>{ rows }</tbody>
        </table>
    </>
}

async function *Catcher() {
    let monsters = do {
        try {
            const { data : { caught } } = await axios.get(`/api/caught`)
            fromJS(caught)
        } catch(e) { console.log({ e }); Map() }
    }
    let selected;
    let infoBox = <i style="color:#ffb6c1;font-size:14px;">✨ Select a Pokémon to see its info~ ✨</i>
    let suggestions = []

    const options = do {
        try {
            const { data : { names } } = await axios.get('/api/names')
            fromJS(names).map(x => <option key={ x } value={ x }>{ x }</option>)
        } catch(e) { console.log({ e }) }
    }
    async function onChange({ target : { value : name } }) {
        const { data : { info } } = await axios.get(`/api/info/${name}`)
        infoBox = <dl id="info-box">
            { fromJS(info).entrySeq().map(([k, v]) => [
                <dt>{ k }</dt>,
                <dd>{ v }</dd>
            ]).flatten() }
        </dl>
        this.refresh()
    }
    const onSearch = debounce(async function(value) {
        if (!value) {
            suggestions = []
            this.refresh()
            return
        }
        try {
            const { data : { results } } = await axios.get(`/api/search?q=${encodeURIComponent(value)}`)
            suggestions = results
            this.refresh()
            if (results.includes(value.toLowerCase())) {
                selected.value = value.toLowerCase()
                await onChange.call(this, { target: { value: value.toLowerCase() } })
            }
        } catch(e) { console.log({ e }) }
    }, 300)
    async function onClick() {
        await axios.put(`/api/catch`, { name: selected.value })
        monsters = do {
            const { data : { caught } } = await axios.get(`/api/caught`)
            fromJS(caught)
        }
        this.refresh()
    }

    for ({} of this)
        yield <>
            <Listing monsters={ monsters } />
            <h2>🌸 Catch a Pokémon 🌸</h2>
            <input
                id="search"
                type="text"
                placeholder="🔍 search pokémon~ (e.g. char, eev…)"
                list="search-suggestions"
                onInput={ e => onSearch.call(this, e.target.value) }
            />
            <datalist id="search-suggestions">
                { suggestions.map(name => <option key={ name } value={ name } />) }
            </datalist>
            <select
                id="catcher"
                onChange={ onChange.bind(this) }
                ref={el => { selected = el }}
            >
                { options }
            </select>
            { infoBox }
            <button
                id="catcher"
                onClick={ onClick.bind(this) }
            >
                ★ CATCH! ★
            </button>
        </>
}

const App = () => {
    return <>
        <style>{ GLOBAL_STYLE }</style>
        <div id="page-wrap">
            <marquee class="top-marquee" behavior="scroll" direction="left" scrollamount="4">
                ✨💖 welcome 2 my pokemon page!! 💖✨ &nbsp;&nbsp; ~*~ best viewed in 800x600 ~*~ &nbsp;&nbsp; 💕 kawaii desu ne~!! 💕 &nbsp;&nbsp; ☆ gotta catch em all ☆ &nbsp;&nbsp; 🌸 made with luv 🌸 &nbsp;&nbsp; ✨💖 welcome 2 my pokemon page!! 💖✨ &nbsp;&nbsp;
            </marquee>

            <div class="sprite-row">
                <img src={ SPRITES.pikachu }    width="80"  height="80"  alt="pikachu"    title="pikachu~!" />
                <img src={ SPRITES.clefairy }   width="64"  height="64"  alt="clefairy"   title="clefairy~!" />
                <span class="star-deco">⭐</span>
                <h1 class="site-title">
                    ✨ A Pokémon Project ✨
                    <span class="subtitle">~ catch &amp; collect ~</span>
                </h1>
                <span class="star-deco reverse">🌟</span>
                <img src={ SPRITES.jigglypuff } width="64"  height="64"  alt="jigglypuff" title="jigglypuff~!" />
                <img src={ SPRITES.eevee }      width="80"  height="80"  alt="eevee"      title="eevee~!" />
            </div>

            <div id="app">
                <Catcher />
            </div>

            <div class="page-footer">
                <div class="sprite-row" style="margin:4px 0">
                    <img src={ SPRITES.togepi } width="48" height="48" alt="togepi" title="togepi~!" />
                    <img src={ SPRITES.mew }    width="64" height="64" alt="mew"    title="mew~!" />
                    <img src={ SPRITES.togepi } width="48" height="48" alt="togepi" title="togepi~!" />
                </div>
                <div class="footer-buttons">
                    <span class="btn-88x31">✨ kawaii ✨</span>
                    <span class="btn-88x31">💕 pokemon 💕</span>
                    <span class="btn-88x31">★ best site ★</span>
                </div>
                <div class="visitor-counter">👁 visitors: 00004869 👁</div>
                <marquee class="footer-marquee" behavior="scroll" direction="right" scrollamount="2">
                    💖 thx 4 visiting~!! please sign my guestbook!! 💖 &nbsp; ✨ ur amazing ✨ &nbsp; 🌸 come back soon!! 🌸
                </marquee>
            </div>
        </div>
    </>
}

await renderer.render(<App />, document.body)
