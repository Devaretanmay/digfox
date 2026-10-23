from repository import find_invoice


def get_invoice(connection, tenant_id, invoice_id):
    row = find_invoice(connection, invoice_id)
    if row is None:
        return None
    return {"tenant_id": row[0], "invoice_id": row[1], "total": row[2]}
