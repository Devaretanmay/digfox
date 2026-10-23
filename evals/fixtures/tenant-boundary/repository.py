def find_invoice(connection, invoice_id):
    return connection.execute(
        "SELECT tenant_id, invoice_id, total FROM invoices WHERE invoice_id = ?",
        (invoice_id,),
    ).fetchone()
