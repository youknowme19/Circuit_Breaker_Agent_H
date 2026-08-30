from backend.app.storage.repository import repository

def get_account_tool(account_id: str):
    account = repository.get_account(account_id)
    if not account:
        return {"error": f"Account '{account_id}' not found"}
    txs = repository.get_transactions_for_account(account_id)
    daily_spent = sum(t.amount for t in txs if t.source_account == account_id and t.status == "EXECUTED")
    return {
        "account": account,
        "daily_spent_total": daily_spent
    }
