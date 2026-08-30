from backend.app.storage.repository import repository

def get_transaction_history_tool(account_id: str, limit: int = 10):
    txs = repository.get_transactions_for_account(account_id)
    return [t.model_dump() for t in txs[:limit]]


def get_transaction_tool(action_id: str):
    for tx in repository.list_transactions():
        if tx.action_id == action_id:
            return tx.model_dump()
    return {"error": f"Transaction for action '{action_id}' not found"}
