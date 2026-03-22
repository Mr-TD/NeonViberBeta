# Neon Viper 2026

A modern, visually stunning reimagining of the classic Nokia Snake game. Built as a single-page HTML5 Canvas application with a Python Flask backend.

## Chosen Vertical
**Web Game Development (Retro Reimagined)**
The goal was to take a beloved childhood classic and elevate it to modern 2026 standards, prioritizing premium aesthetics, rich user engagement (power-ups, combo systems, cosmetics), and persistent background progression.

## Approach and Logic
- **High-Performance Canvas Rendering**: The core game is built on a direct HTML5 `<canvas>` element. Using a `requestAnimationFrame` 60fps loop ensures smooth snake interpolation and responsive particle effects without overwhelming the DOM.
- **State-Driven Architecture**: The game logic in `game.js` is strictly tied to a `gameState` object. The UI and rendering functions do not calculate logic; they only paint based on the current state.
- **Lightweight Backend**: We chose Flask coupled with standard `sqlite3` to manage user profiles. This allowed us to build robust player persistence (currency, high scores, cosmetics) with zero configuration overhead, keeping the application fast and portable.

## How the Solution Works
1. **Application Server**: Running `python app.py` starts a Flask web server that handles API endpoints mapping to a local `game.db` SQLite database.
2. **Session and Profile UI**: Upon opening `localhost:5000`, the frontend checks `/api/profile`. If the user has no session cookie, a floating Glassmorphism modal prompts them to either select an existing profile (sorted by high score) or instantly create a new one. 
3. **Core Game Loop**: Once past the classic Nokia boot screen, the game listens to Arrow Keys / WASD. It updates the snake's grid coordinates, checks for collision (walls, self, or bombs), and evaluates interactions (normal food, diamond food, power-ups).
4. **Data Synchronization**: As the player earns gems or beats their high score, lightweight asynchronous POST requests (`/api/save`) are fired off to seamlessly save their progress to the database without interrupting gameplay.

## Assumptions Made
- **Frictionless Authentication**: It is assumed that for a casual browser game, users do not want to fill out complex registration forms. Thus, the profile system operates solely on distinct usernames to get players into the action immediately.
- **Local / Single-Instance Deployment**: We assumed this application will be run locally or on a single isolated server instance, which makes SQLite the perfect, frictionless choice for the database.
- **Modern Browser Support**: We assumed the target audience is utilizing a modern browser capable of supporting ES6 JavaScript, async/await `fetch` logic, and Web Audio APIs for the synthesized retro sound effects.
