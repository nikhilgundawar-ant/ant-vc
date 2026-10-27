# Template: CRM change proposal

```json
{"id": "<proposal id>", "type": "crm_update", "record": {"kind": "deal", "id": "<CRM id>", "name": "<company>"},
 "fields": [{"field": "next_step", "current": "Read data room", "proposed": "Reference calls with two NBFCs"},
            {"field": "next_step_due", "current": "2026-10-20", "proposed": "2026-10-27"}],
 "why": "Agreed on the 21 Oct call", "source_url": "<notes link>", "status": "proposed"}
```

Allowed fields: stage, next_step, next_step_due, note, last_contact. Statuses: proposed, approved, applied, failed.
