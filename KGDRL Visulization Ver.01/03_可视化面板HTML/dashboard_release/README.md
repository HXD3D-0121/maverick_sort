# Smart Wave Allocation Dashboard - Release Package

## 📦 Package Contents

| File | Description |
|------|-------------|
| `smart_wave_dashboard.html` | Chinese version |
| `smart_wave_dashboard_en.html` | English version |
| `data/` | Pipeline output data (JSON + plots) |

## 🚀 How to Open

### Method 1: Direct Open (Easiest)
Simply **double-click** either HTML file. It runs entirely in the browser with zero setup.

Supported browsers: Chrome, Edge, Firefox, Safari.

### Method 2: Local Server (For team viewing)
If sharing over LAN with teammates:

```bash
cd dashboard_release
python -m http.server 8080
```

Then visit `http://localhost:8080/smart_wave_dashboard_en.html`

Teammates on the same network can visit `http://YOUR_IP:8080/...`

### Method 3: GitHub Pages (Public Link)
1. Create a GitHub repo
2. Upload both HTML files to the repo
3. Go to Settings → Pages → Source: Deploy from branch (main)
4. Access at `https://YOURNAME.github.io/REPO/smart_wave_dashboard_en.html`

## 🎮 Dashboard Features

- **Real-Time Simulation**: Play/pause/reset wave allocation animation
- **Warehouse Zone Map**: Live 2×4 grid showing active zones
- **Wave Management**: Complete wave history with temp/zone tags
- **Algorithm Comparison**: PPO vs 5 heuristic baselines (charts + table)
- **Exception Alerts**: Real-time temp-mixing and capacity warnings
- **Labor Load**: Header stat showing simulated picker utilization

## 📊 Data Source

All visualization data is embedded. No backend required.
- Order distributions: from pharmaceutical casebook empirical stats
- PPO results: from 120-episode training + 20-instance evaluation
- Heuristic baselines: FCFS, TEMP_FIRST, ZONE_NN, EDD, TZU
