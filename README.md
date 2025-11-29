# BlackBox v3: Sports Betting Analytics Framework

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**BlackBox v3** is an advanced quantitative sports betting framework that moves beyond simple statistical regression. It utilizes a **Three-Domain Architecture** to separate fundamental skill, narrative context, and variance simulation, creating a "glass box" prediction engine.

The system is deployed as a persistent service using **Discord** as the frontend interface and **Google Firestore** for state management and bankroll tracking.

---

## 🏗 Architecture

The framework splits analysis into three distinct domains:

1.  **Domain I (FairLine):** Raw fundamental skill modeling (xG, Power Ratings).
2.  **Domain II (GameStory):** Contextual adjustments (Motivation, Injuries, Rivalries, Schedule Congestion).
3.  **Domain III (Variance):** Volatility injection and Monte Carlo simulation parameters.

**Stack:**
* **Core:** Python 3.11, Pandas, NumPy, Pydantic
* **Interface:** Discord.py (Bot)
* **Database:** Google Firestore (NoSQL)
* **Infrastructure:** Docker

---

## 🚀 Quick Start

### Prerequisites
* Python 3.11+
* Docker (optional, for production)
* Firebase Service Account Credentials
* Discord Bot Token

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/waltspence/blackbox-v3.git](https://github.com/waltspence/blackbox-v3.git)
    cd blackbox-v3
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Setup:**
    Create a `.env` file in the root directory:
    ```ini
    DISCORD_TOKEN=your_discord_bot_token
    FIREBASE_CREDENTIALS_JSON=service-account.json
    ODDS_API_KEY=your_odds_api_key
    ```

4.  **Run the Bot:**
    ```bash
    python bot.py
    ```

---

## 📂 Project Structure

```text
blackbox-v3/
├── frameworks/             # Core Analytics Logic
│   ├── game_story.py       # Domain II: Narrative Context Engine
│   ├── three_domain.py     # Pipeline Orchestrator
│   └── utils.py            # Math helpers (clamp, probability calc)
├── services/               # Infrastructure Adapters
│   ├── db.py               # Firebase/Firestore Interface
│   └── data_fetcher.py     # External API Ingress
├── bot/                    # Discord Interface
│   ├── main.py             # Bot Entry Point
│   └── cogs/               # Command Modules
├── tests/                  # Unit Tests
├── docs/                   # Documentation
├── Dockerfile              # Production Build
└── requirements.txt        # Dependencies
