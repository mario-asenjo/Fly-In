"""Evaluator-safe formatting for simulation turns."""

from flyin.simulation.model import MovementFact, TransitFact, TurnFact


def format_turn(facts: tuple[TurnFact, ...]) -> str:
    """Format one evaluator-safe output line from movement facts."""
    return " ".join(
        _format_fact(fact)
        for fact in sorted(facts, key=lambda fact: fact.drone_id)
    )


def _format_fact(fact: TurnFact) -> str:
    if isinstance(fact, MovementFact):
        return f"D{fact.drone_id}-{fact.destination.name}"
    if isinstance(fact, TransitFact):
        return f"D{fact.drone_id}-{fact.origin.name}-{fact.destination.name}"
    raise TypeError(f"unsupported turn fact: {type(fact).__name__}")
