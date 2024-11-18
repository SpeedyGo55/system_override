# System Override
A top-down 2D shooter game where you try to defeat as many evil Robots as possible. The game is made with PyGame and Python.

## Installation
1. Clone the repository
```bash
git clone https://github.com/SpeedyGo55/system_override.git
```
2. Install the required packages
```bash
pip install -r requirements.txt
```
3. Make a config.json file in the root directory with the following content:
```json
{
  "LEADERBOARD_SECRET": "<Dreamlo Leaderboard Secret Key>",
  "LEADERBOARD_PUBLIC": "<Dreamlo Leaderboard Public Key>",
  "LEADERBOARD_URL": "http://dreamlo.com/lb/"
}
```
You can get the keys for free from [Dreamlo](http://dreamlo.com/)
4. Run the game
```bash
python main.py
```

## Controls
- Move: WASD
- Shoot: Left Mouse Button
- Aim: Mouse Cursor

With Esc you can go back to the Start Screen.

## Features
- 3 Weapons you can pick up. The enemies can spawn with these but cant pick them Up
- Name Input for the Online Dreamlo Leaderboard
- Dreamlo Leaderboard Integration

