# Invoice access contract
An invoice must be returned only when its tenant matches the authenticated caller's tenant. Invoice numeric IDs are not globally unique. A missing or unauthorized invoice must return None. The reviewer should inspect proposed.patch and service.py and identify the cross-tenant access regression without changing files.
