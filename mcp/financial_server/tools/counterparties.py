from backend.app.storage.repository import repository

def get_counterparty_tool(counterparty_id: str):
    cp = repository.get_counterparty(counterparty_id)
    if not cp:
        return {"error": f"Counterparty '{counterparty_id}' not found", "verified": False}
    return cp
