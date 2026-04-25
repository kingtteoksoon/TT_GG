import unittest

from src.auction_pricing import (
    Player,
    TournamentConfig,
    calculate_scarcity,
    estimate_starting_prices_without_ai,
    validate_tier_name,
)


class PricingTests(unittest.TestCase):
    def test_validate_tier_name_rejects_digits(self):
        with self.assertRaises(ValueError):
            validate_tier_name("다이아1")

    def test_calculate_scarcity(self):
        config = TournamentConfig(teams_count=8, slots_per_team_by_position={"타격대": 2})
        scarcity = calculate_scarcity("타격대", supply=10, config=config)
        self.assertAlmostEqual(scarcity, 1.6)

    def test_estimate_starting_prices_without_ai(self):
        players = [
            Player("A", "다이아", "타격대", "캐릭1"),
            Player("B", "실버", "타격대", "캐릭2"),
        ]
        config = TournamentConfig(teams_count=8, slots_per_team_by_position={"타격대": 2})

        prices = estimate_starting_prices_without_ai(
            players,
            tier_rank={"다이아": 4, "실버": 2},
            tier_base_prices={"다이아": 1000, "실버": 500},
            position_adjustments={"타격대": 1.0},
            config=config,
            seed=1,
        )

        self.assertEqual(set(prices.keys()), {"A", "B"})
        self.assertTrue(prices["A"] > prices["B"])


if __name__ == "__main__":
    unittest.main()
