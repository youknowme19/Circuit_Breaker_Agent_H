from typing import Tuple, List
from backend.app.models.action import StructuredFinancialAction
from backend.app.risk.graph import fraud_graph

class RiskEngine:
    """Combines FraudGraph signals into risk score."""

    def evaluate(self, action: StructuredFinancialAction) -> Tuple[float, List[str]]:
        return fraud_graph.analyze_risk(
            source=action.source_account,
            destination=action.destination_account,
            amount=action.amount
        )

risk_engine = RiskEngine()
