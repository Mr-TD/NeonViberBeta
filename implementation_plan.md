# 🐍 Nokia Snake Reimagined — Implementation Plan

Reimagine the classic Nokia Snake as a modern, visually stunning browser game with power-ups, bombs, an in-game shop, and premium aesthetics — all in a single-page HTML5 Canvas app.

## Proposed Changes

### Game Structure (3 files)

#### [NEW] [index.html](file:///x:/PromptWar/index.html)
Main HTML entry point with canvas, HUD overlay, shop modal, and game-over screen.

#### [NEW] [style.css](file:///x:/PromptWar/style.css)
Dark neon retro-modern theme with glassmorphism panels, glow effects, animations, and responsive layout.

#### [NEW] [game.js](file:///x:/PromptWar/game.js)
All game logic in one file (~1200 lines). Sections:

| Section | Details |
|---|---|
| **Game Engine** | Canvas rendering, 60fps game loop, snake movement (Arrow Keys + WASD), grid-based collision |
| **Food System** | Standard food dots (score +10), golden food (score +25) |
| **Bomb System** | Red/black bombs spawn randomly; collision deducts 30 points; pulsing warning animation |
| **Power-Ups** | 🔥 Fire (fire trail visuals, bombs disabled 8s) · 🧊 Ice (ice visuals, magnet pull radius 8s) · ⚡ Speed (2× speed 6s) · 🛡️ Shield (invincible 8s, glow outline) · 👻 Ghost (pass through self 8s) |
| **Bonus Dots** | Golden dots that move randomly; worth +50 pts and +5 gems |
| **Combo System** | Eat food within 2s of last eat → combo multiplier (×2, ×3, ×4…) with popup text |
| **Gems & Shop** | Earn gems from bonus dots and combos. Shop has 6 skins (Neon, Lava, Ocean, Galaxy, Rainbow, Gold). Purchases persist in `localStorage` |
| **Level System** | Every 100 points → level up, speed increases slightly, more bombs spawn |
| **HUD** | Score, High Score, Gems, Active Power, Level, Combo counter |
| **Nokia Boot Screen** | Retro-style splash screen with "NOKIA" text and classic ringtone-style animation, then transitions into modern UI |
| **Particles** | Burst particles on eating food, collecting power-ups, bomb hits |
| **Pause** | Press `P` or `Space` to pause |

---

### Feature Details

**Power-Up Behavior:**
- Power-up dots spawn every 15–25 seconds at random positions
- Only one power-up active at a time (new one replaces old)
- Visual snake transformation lasts for the power-up duration
- Status bar shows active power with countdown timer

**Bomb Behavior:**
- Bombs appear after level 2
- 1–3 bombs on screen at a time, respawn every 10–20s
- Score deduction: −30 points (cannot go below 0)
- Screen shake + red flash on bomb hit

**Shop Skins (6 skins):**

| Skin | Cost | Look |
|---|---|---|
| Classic Green | Free (default) | Nokia green |
| Neon Cyan | 50 gems | Cyan with glow |
| Lava Red | 100 gems | Red-orange gradient |
| Ocean Blue | 100 gems | Blue-teal shimmer |
| Galaxy Purple | 200 gems | Purple with star particles |
| Rainbow | 300 gems | Cycling hue |

---

## Verification Plan

### Browser Testing (Automated via browser subagent)
1. Open `x:\PromptWar\index.html` in the browser
2. Verify the Nokia boot screen appears and transitions to the game
3. Verify snake moves with arrow keys
4. Verify food spawns and score increases on eating
5. Verify power-up dots spawn and apply visual effects
6. Verify bombs deduct score and show warning
7. Open the shop, verify skin prices and equip flow
8. Verify game over screen shows on collision
9. Verify restart works correctly

### Manual Verification (User)
- Play through a few rounds to confirm all power-ups feel right
- Check that gem persistence works across page refreshes
- Confirm responsive layout on different window sizes
