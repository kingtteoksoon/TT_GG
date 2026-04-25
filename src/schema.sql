-- 공통 메타
CREATE TABLE games (
  id INTEGER PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL
);

CREATE TABLE tournaments (
  id INTEGER PRIMARY KEY,
  game_id INTEGER NOT NULL REFERENCES games(id),
  season_name TEXT NOT NULL,
  teams_count INTEGER NOT NULL,
  team_budget_cap INTEGER NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE teams (
  id INTEGER PRIMARY KEY,
  tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
  team_name TEXT NOT NULL,
  remaining_budget INTEGER NOT NULL
);

CREATE TABLE players (
  id INTEGER PRIMARY KEY,
  tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
  username TEXT NOT NULL,
  highest_tier TEXT NOT NULL,
  position TEXT NOT NULL,
  preferred_character TEXT,
  created_at TEXT NOT NULL
);

-- 시작가 산정 로그(알고리즘/AI)
CREATE TABLE price_estimation_logs (
  id INTEGER PRIMARY KEY,
  tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
  player_id INTEGER NOT NULL REFERENCES players(id),
  method TEXT NOT NULL, -- AI / ALGORITHM
  model_name TEXT,
  prompt_snapshot TEXT,
  debate_summary TEXT,
  tier_base_price REAL,
  position_adjustment REAL,
  scarcity REAL,
  random_factor REAL,
  estimated_price REAL NOT NULL,
  decided_by_admin INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

-- 경매
CREATE TABLE auction_items (
  id INTEGER PRIMARY KEY,
  tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
  player_id INTEGER NOT NULL REFERENCES players(id),
  starting_price REAL NOT NULL,
  final_price REAL,
  winner_team_id INTEGER REFERENCES teams(id),
  status TEXT NOT NULL, -- OPEN / SOLD / CANCELED
  created_at TEXT NOT NULL,
  closed_at TEXT
);

CREATE TABLE bids (
  id INTEGER PRIMARY KEY,
  auction_item_id INTEGER NOT NULL REFERENCES auction_items(id),
  team_id INTEGER NOT NULL REFERENCES teams(id),
  bid_amount REAL NOT NULL,
  bid_time TEXT NOT NULL
);

-- 게임별 포지션 수요 정의
CREATE TABLE position_requirements (
  id INTEGER PRIMARY KEY,
  tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
  position TEXT NOT NULL,
  slots_per_team INTEGER NOT NULL
);
