"""Evaluator-safe formatting for simulation turns."""

from flyin.simulation.model import TurnFact


def format_turn(facts: tuple[TurnFact, ...]) -> str:
    """Format one evaluator-safe output line from movement facts."""
    return " ".join(
        fact.token for fact in sorted(facts, key=lambda fact: fact.drone_id)
    )
