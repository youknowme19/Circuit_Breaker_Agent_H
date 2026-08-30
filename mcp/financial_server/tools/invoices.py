from backend.app.storage.repository import repository

def get_invoice_tool(invoice_id: str):
    inv = repository.get_invoice(invoice_id)
    if not inv:
        return {"error": f"Invoice '{invoice_id}' not found"}
    return inv


def list_invoices_tool():
    return repository.list_invoices()
