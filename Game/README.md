# Typing Speed Battle

A modern cyberpunk typing speed game with two delivery targets:

- The original Python/Pygame desktop version.
- A browser-ready web version in [web/](web).

## What Changed

The desktop Pygame build is still available, but the deployable experience is now the browser version. That version fixes the button/input flow, adds responsive HTML controls, stores the leaderboard in `localStorage`, and is suitable for GitHub Pages, Netlify, Vercel, or any static host.

## Folder Structure

```text
Game/
  main.py
  game.py
  ui_manager.py
  word_manager.py
  player_stats.py
  leaderboard_manager.py
  asset_utils.py
  config.py
  requirements.txt
  README.md
  assets/
    fonts/
    sounds/
    words.txt
  leaderboard/
    scores.json
  web/
    index.html
    styles.css
    main.js
    game.js
    ui_manager.js
    word_manager.js
    player_stats.js
    leaderboard_manager.js
    audio_manager.js
    words.txt
```

## Run the Desktop Version

1. Open the `Game` folder in VS Code.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate it on Windows:
   ```bash
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the desktop game:
   ```bash
   python main.py
   ```

## Run the Website Version Locally

1. Open the `web` folder in VS Code.
2. Start a local server from the `web` folder. One simple option is:
   ```bash
   python -m http.server 8000
   ```
3. Open `http://127.0.0.1:8000/` in your browser.

## Deploy the Website

1. Upload everything inside `web/` to GitHub Pages, Netlify, Vercel, or any static hosting service.
2. Keep the file names as-is so the ES module imports continue to work.
3. If you want to host from the repository root instead, copy `web/index.html` and the JS/CSS files into your site root and keep `assets/words.txt` available at the matching relative path.

## Controls

- Type the word shown in the center.
- `Enter` submits the current attempt.
- `Backspace` removes a character.
- `ESC` pauses or resumes the game.
- Use the buttons, mode pills, and volume control in the browser UI.

## Future Improvement Ideas

- Add editable player names for leaderboard entries.
- Add more music themes and richer sound effects.
- Add a practice mode with no timer.
- Add animated boss-rush or survival modes.
- Add cloud saves for the leaderboard.
