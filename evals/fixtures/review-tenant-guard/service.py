def get_invoice(invoice_id, tenant_id, repository):
    """Return the invoice owned by tenant_id, or None."""
    return repository.get_by_id_and_tenant(invoice_id, tenant_id)
