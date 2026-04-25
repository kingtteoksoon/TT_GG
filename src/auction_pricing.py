from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class Player:
    username: str
    highest_tier: str
    position: str
    preferred_character: str


@dataclass(frozen=True)
class TournamentConfig:
    teams_count: int
    slots_per_team_by_position: Dict[str, int]


def validate_tier_name(tier: str) -> None:
    """티어 이름은 숫자를 포함하면 안 된다."""
    if any(ch.isdigit() for ch in tier):
        raise ValueError(f"숫자가 포함된 티어는 허용되지 않습니다: {tier}")


def sort_players_by_tier(players: Sequence[Player], tier_rank: Dict[str, int]) -> List[Player]:
    return sorted(players, key=lambda p: tier_rank.get(p.highest_tier, 0), reverse=True)


def classify_by_position(players: Sequence[Player]) -> Dict[str, List[Player]]:
    grouped: Dict[str, List[Player]] = {}
    for p in players:
        grouped.setdefault(p.position, []).append(p)
    return grouped


def calculate_scarcity(
    position: str,
    supply: int,
    config: TournamentConfig,
) -> float:
    if supply <= 0:
        raise ValueError(f"공급 인원이 0 이하입니다: position={position}, supply={supply}")
    demand = config.teams_count * config.slots_per_team_by_position.get(position, 0)
    return demand / supply


def calculate_price(
    *,
    tier_base_price: float,
    position_adjustment: float,
    scarcity: float,
    rng: Random,
) -> float:
    if not (0.5 <= position_adjustment <= 1.0):
        raise ValueError("포지션 보정값은 0.5~1.0 범위여야 합니다.")

    random_factor = rng.uniform(0.9, 1.1)
    return tier_base_price * position_adjustment * scarcity * random_factor


def estimate_starting_prices_without_ai(
    players: Sequence[Player],
    *,
    tier_rank: Dict[str, int],
    tier_base_prices: Dict[str, float],
    position_adjustments: Dict[str, float],
    config: TournamentConfig,
    seed: int = 42,
) -> Dict[str, float]:
    """
    AI 연결이 없을 때 요구된 알고리즘으로 시작가를 계산한다.

    단계:
    1) 티어 기준 내림차순 정렬
    2) 포지션별 분류
    3) 포지션별 인원 수 확인(공급)
    4) 운영진이 입력한 티어 기본가격/포지션 보정값 적용
    5) 희소성(Demand/Supply) 계산
    6) 랜덤 계수(0.9~1.1) 반영
    """
    rng = Random(seed)

    for tier_name in tier_base_prices:
        validate_tier_name(tier_name)

    sorted_players = sort_players_by_tier(players, tier_rank)
    grouped = classify_by_position(sorted_players)

    prices: Dict[str, float] = {}
    for p in sorted_players:
        if p.highest_tier not in tier_base_prices:
            raise KeyError(f"티어 기본가격이 없습니다: {p.highest_tier}")
        if p.position not in position_adjustments:
            raise KeyError(f"포지션 보정값이 없습니다: {p.position}")

        supply = len(grouped[p.position])
        scarcity = calculate_scarcity(p.position, supply, config)
        price = calculate_price(
            tier_base_price=tier_base_prices[p.highest_tier],
            position_adjustment=position_adjustments[p.position],
            scarcity=scarcity,
            rng=rng,
        )
        prices[p.username] = round(price, 2)

    return prices
