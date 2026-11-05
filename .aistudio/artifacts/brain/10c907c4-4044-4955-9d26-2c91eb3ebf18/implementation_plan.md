# Sansad Showdown: The Great Kursi Fight (Exact 1:1 Replica)

A complete, pixel-for-pixel, word-for-word, and asset-for-asset replica of **Sansad Showdown: The Great Kursi Fight** (`fightkaro.com`), preserving the exact HTML DOM, CSS styling, Three.js WebGL combat engine, 3D rigged GLB fighter models, original voiceovers/SFX, and live WebRTC multiplayer room signaling.

## User Review & Critical Decisions

> [!IMPORTANT]
> Both key architectural choices have been confirmed and incorporated into this plan:

- **Confirmed Decision 1 — Full Local Asset Mirroring**: All original `.glb` 3D character models (desktop and mobile variants), Draco WASM/JS decoders, `.webp` character portraits, `.mp3` voiceovers, music tracks, sound effects, and `.mp4` portal video assets will be mirrored locally into the application's static asset tree, backed by a transparent proxy fallback to ensure zero missing bytes.
- **Confirmed Decision 2 — Full WebRTC Signaling Server (`/api/room` & `/api/ice`)**: An Express backend will implement the exact signaling protocol expected by the game's multiplayer module (`POST /api/room`, `GET /api/room`, `POST /api/room?action=answer`, long-polling `GET /api/room?code=...&secret=...&wait=25`, `DELETE /api/room`, and `POST/GET /api/room?action=signal`) so 4-character room codes and "Play With a Friend" work end-to-end.

---

## 1. Overview & Core Concept

- **What It Does**: Delivers the complete *Sansad Showdown: The Great Kursi Fight* 2.5D arcade fighting experience in the browser with zero alterations to text, layout, shaders, lighting, animations, or controls.
- **Target Audience / Persona**: Players looking for the exact viral arcade parody fighter experience with both single-player CPU/Boss progression ("Beat Mbapu to open the portal") and live P2P online multiplayer.
- **Key Value**: 100% fidelity to the original production build—every DOM element, CSS rule, font (`Bebas Neue` & `Teko`), 3D skeletal rig, Shakti super animation, Nirmala Budget assist, and Breaking Bakwas / Troll Army live newsdesk commentary runs identically.

---

## 2. User Experience & Visual Design

- **Key User Flows**:
  1. **Loading & Title Screen (`#loading` → `#title`)**: Displays the `SANSAD SHOWDOWN: THE GREAT KURSI FIGHT` emblem, asset progress bar, and portal status banner (`Beat Mbapu to open the portal 🔒`), alongside the bilingual English/Hindi legal satire disclaimer modal (`#legal`).
  2. **Character Select (`#select`)**: Fighting-game style grid (`SELECT YOUR NETA`) with 1P and CPU/2P cursors, 3D fighter previews on the left/right flanks, corner nameplates showing party and signature super descriptions, mode toggles (vs CPU, 2P Local, Play With a Friend), and the UPI support modal.
  3. **In-Fight Arcade HUD (`#hud`)**:
     - Top bar with P1/P2 portraits, health bars (`hp-fill` and `hp-trail`), round win pips, and 60-second match timer (`#timer`).
     - Bottom `SHAKTI` super meters (`meter left` / `meter right`) and dynamic combo counters.
     - **Live TV Newsdesk (`#newsdesk`)**: Real-time commentary duel between *Shor Sharma (Breaking Bakwas)* and *Tweety Trollwala (Troll Army)* with a scrolling `BREAKING` news ticker.
     - **Nirmala's Budget Assist (`#budget-meter`)**: Interactive `📕 BUDGET` button (`Key B` / touch button) during boss matches against Mbapu.
     - **Portal Cinema (`#cinema`)**: Full-screen letterboxed cutscene player when unlocking/completing the boss portal.
  4. **Play With a Friend (`#online`)**: Host a room to generate a shareable room code (with WhatsApp share & copy link buttons) or enter a friend's room code to connect over WebRTC DataChannels.

- **Visual Identity & Theme**:
  - *Aesthetic Direction*: High-energy Indian arcade broadcast satire combining 3D cel-shaded/PBR caricatures on the Sansad courtyard stage (including seasonal Diwali Deepotsav diyas, lanterns, and fireworks particle bursts) with broadcast television chyron graphics.
  - *Color Palette & Mood*: Deep obsidian stage framing (`#0a0812`), saffron/gold arcade highlights (`#ff9933`, `#ffd700`), broadcast alert red (`#e0262f`), and fighter-specific party accents.
  - *Typography & Hierarchy*: Original Google Fonts pairing of `Bebas Neue` and `Teko` (`500`, `700`) for arcade headers, health bars, announcements, and news tickers.
  - *Component Styling & Layout*: Full-viewport `<canvas id="game">` layered beneath exact semantic DOM HUD overlays (`#vignette`, `#flash`, `#popups`, `#hud`, `#announce`, `#touch`), plus mobile landscape orientation lock (`#rotate`) and iOS fullscreen swipe helper (`#ios-swipe`).

---

## 3. Key Product Decisions & Trade-Offs

- **Decision 1: Exact Production Bundle & Asset Preservation**
  - *Chosen Approach*: Serve the exact upstream HTML markup, compiled CSS stylesheet (`main-C4DN45Lw.css`), and compiled ES modules (`main-CfQ2THv5.js`, `rooms-CRfnBsqC.js`, `three-CJyKo-TQ.js`) alongside locally mirrored `/models/*.glb`, `/faces/*.webp`, `/draco/*`, and `/assets/*.mp3` files.
  - *Why*: The user explicitly requested that not a single word or pixel be replaced. Running the exact production client bundle with locally mirrored assets guarantees 100% visual, mechanical, and typographic identity.
  - *Alternatives Considered*: Rewriting the UI in React/Tailwind from scratch—rejected because any re-implementation would alter pixels, shaders, animation curves, or wording.

- **Decision 2: Express WebRTC Signaling & Transparent Asset Fallback**
  - *Chosen Approach*: Build an Express server (`server.ts`) on port 3000 that implements the full `/api/room` and `/api/ice` WebRTC signaling state machine in memory, serves the mirrored static files with high-performance caching, and provides an automatic streaming proxy fallback for any dynamic query-string or secondary asset requests.
  - *Why*: Guarantees both offline-ready speed for all 3D models/audio and 100% functional multiplayer room hosting/joining without any 404s.

---

## 4. Technical Architecture & Data Strategy *(Technical Reference)*

### Architecture & Component Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        Browser Client (Port 3000)                          │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Exact DOM Layer (index.html + main-C4DN45Lw.css)                     │  │
│  │  ├─ #loading / #title / #legal (Bilingual Satire Disclaimer)         │  │
│  │  ├─ #select (9 Netas Grid, 1P/CPU Plates, Mode Switcher)             │  │
│  │  ├─ #hud (HP Bars, Timer, Shakti Meters, #newsdesk, #budget-meter)   │  │
│  │  ├─ #online (Host Room Code, WhatsApp Share, Join Form)              │  │
│  │  └─ #cinema (Portal Video Cutscene) & #touch (Mobile Arcade Stick)   │  │
│  └──────────────────────────────────┬───────────────────────────────────┘  │
│                                     │                                      │
│  ┌──────────────────────────────────▼───────────────────────────────────┐  │
│  │ Game & 3D Engine (main-CfQ2THv5.js + three-CJyKo-TQ.js)              │  │
│  │  ├─ Three.js WebGLRenderer (<canvas id="game">) + DRACOLoader        │  │
│  │  ├─ 9 Rigged GLB Fighters + Bulldozer Prop + 35-Joint IK Animator    │  │
│  │  ├─ Sansad Arena + Diwali Deepotsav Fireworks & Diyas System         │  │
│  │  └─ Web Audio Synthesizer + Voiceover & SFX Buffer Manager           │  │
│  └──────────────────────────────────┬───────────────────────────────────┘  │
│                                     │                                      │
│  ┌──────────────────────────────────▼───────────────────────────────────┐  │
│  │ Multiplayer P2P Module (rooms-CRfnBsqC.js)                           │  │
│  │  └─ RTCPeerConnection + Dual DataChannels (ctrl & input)             │  │
│  └──────────────────────────────────┬───────────────────────────────────┘  │
└─────────────────────────────────────┼──────────────────────────────────────┘
                                      │ HTTP REST / Long-Polling
┌─────────────────────────────────────▼──────────────────────────────────────┐
│                     Express Server (server.ts : 3000)                      │
│                                                                            │
│  ├─ GET  /api/ice           → Returns STUN/TURN ICE server configuration   │
│  ├─ POST /api/room          → Creates 4-char room code + secret + SDP offer│
│  ├─ GET  /api/room?code=... → Guest fetches SDP offer or Host long-polls   │
│  ├─ POST /api/room?action=answer → Guest submits SDP answer, wakes Host    │
│  ├─ ALL  /api/room?action=signal → ICE restart offer/answer exchange       │
│  ├─ DELETE /api/room        → Cleans up room state                         │
│  └─ Static & Mirror Layer   → Serves local /models, /faces, /assets, /draco│
└────────────────────────────────────────────────────────────────────────────┘
```

### Data Model & State

- **Client Progression State (`localStorage['sansad-showdown:bapu-v1']`)**:
  - Tracks `streak`, `unlocked` (Mbapu boss playable unlock), `bestSeconds`, `bestDamage`, `peaceWins`, and `portalSeen`.
- **Server Room Signaling Store (`Map<string, RoomSession>`)**:
  - `code`: 4-character alphanumeric code from alphabet `ABCDEFGHJKMNPQRSTUVWXYZ23456789`.
  - `secret`: Cryptographic session secret (`sid`) shared between host and guest for ICE restart signaling.
  - `offer` / `answer`: WebRTC `RTCSessionDescriptionInit` payloads.
  - `signals`: Indexed map of ICE restart offers and answers (`offer:N`, `answer:N`) with long-polling waiter queues.
  - `expiresAt`: 10-minute TTL with automatic cleanup.

### Interactive Component & State Mapping

- **Title & Legal Modal (`#legal-ok`, `#title`)**: Clicking `I UNDERSTAND · CONTINUE` dismisses the legal notice, initializes the Web Audio context, and transitions from `#title` to `#select`.
- **Character Selection (`#select`, `#plate-p1`, `#plate-p2`)**: Hovering/clicking portraits updates the 3D preview models, party badges, and super descriptions; confirming starts the match or opens the `#online` room flow.
- **Combat & HUD (`#hud`, `#budget-meter`, `#pause-btn`)**: Real-time frame loop updates HP bars, Shakti meters, combo popups, newsdesk anchor dialogue, and triggers cinematic camera sequences on `SUPER` or `BUDGET` activation.
- **Online Multiplayer (`#on-host`, `#on-join-form`, `#on-wa`, `#on-copy`)**: Hosting creates a room via `POST /api/room`, displays the 4-character code, and long-polls until a guest submits their answer via `#on-join-form`, establishing direct WebRTC `ctrl` and `input` DataChannels.
