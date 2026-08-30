import networkx as nx
from typing import Dict, List, Tuple

class FraudGraph:
    """NetworkX-based graph intelligence engine for behavioral risk scoring."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self._seed_default_graph()

    def reset(self):
        """Reset graph to initial seed state."""
        self.graph = nx.DiGraph()
        self._seed_default_graph()

    def _seed_default_graph(self):
        """Seed initial transaction topology for detection of synthetic layering ($A -> B -> C -> D -> E$)."""
        # Layering path nodes
        nodes = ["ACC-001", "ACC-101", "ACC-102", "ACC-103", "ACC-104", "ACC-991"]
        for n in nodes:
            self.graph.add_node(n, type="account")

        # Synthetic layering edges
        edges = [
            ("ACC-001", "ACC-101", 6000.0),
            ("ACC-101", "ACC-102", 5900.0),
            ("ACC-102", "ACC-103", 5800.0),
            ("ACC-103", "ACC-104", 5700.0),
            ("ACC-104", "ACC-991", 5600.0),
        ]
        for src, dst, amt in edges:
            self.graph.add_edge(src, dst, amount=amt)

    def add_transaction_edge(self, source: str, destination: str, amount: float):
        if not self.graph.has_node(source):
            self.graph.add_node(source, type="account")
        if not self.graph.has_node(destination):
            self.graph.add_node(destination, type="account")
        self.graph.add_edge(source, destination, amount=amount)

    def analyze_risk(self, source: str, destination: str, amount: float) -> Tuple[float, List[str]]:
        """Returns risk score in [0.0, 1.0] and array of risk signal codes."""
        risk_score = 0.10
        signals = []

        # Check for direct destination to known suspicious high-degree node
        if destination == "ACC-991":
            risk_score += 0.40
            signals.append("HIGH_RISK_DESTINATION_NODE")

        # Temporarily add edge to analyze topology
        temp_g = self.graph.copy()
        temp_g.add_edge(source, destination, amount=amount)

        # Check path length / layering chain
        try:
            paths = list(nx.all_simple_paths(temp_g, source=source, target=destination, cutoff=6))
            max_len = max(len(p) for p in paths) if paths else 1
            if max_len >= 4:
                risk_score += 0.45
                signals.append("CIRCULAR_LAYERING_PATTERN")
        except Exception:
            pass

        # High amount outlier check
        if amount >= 45000.0:
            risk_score += 0.35
            signals.append("HIGH_AMOUNT_OUTLIER")

        final_score = min(round(risk_score, 2), 0.99)
        return final_score, signals

    def get_graph_export(self) -> Dict:
        """Export graph structure for frontend rendering."""
        nodes = []
        for n, data in self.graph.nodes(data=True):
            degree = int(self.graph.degree(n))
            suspicious = n == "ACC-991" or n.startswith("ACC-10")
            nodes.append({
                "id": n,
                "label": n,
                "type": data.get("type", "account"),
                "degree": degree,
                "transaction_count": degree,
                "risk_score": 0.9 if suspicious else min(0.2 + degree * 0.05, 0.7),
                "suspicious": suspicious,
            })
        edges = []
        for src, dst, data in self.graph.edges(data=True):
            edges.append({"source": src, "target": dst, "amount": data.get("amount", 0.0)})
        return {"nodes": nodes, "edges": edges, "layering_paths": [["ACC-001", "ACC-101", "ACC-102", "ACC-103", "ACC-104", "ACC-991"]]}

fraud_graph = FraudGraph()
