# R1 SDK Backlog

Cross-session tracking for SDK features needed by r1-scripts or other consumers.

## Completed

- [x] Module renames: `wlans` → `wifi_networks`, `vlans` → `vlan_pools`, `l3acl` → `l3_acl_policies`, `AccessPoints` → `APs` (0.3.0)
- [x] `list_all()` auto-pagination for 8 modules (0.3.0)
- [x] 854 unit tests, 99% coverage (0.3.0)
- [x] MacRegistrationPools module — pool CRUD, registration CRUD, CSV import, policy set associations (0.5.0)
- [x] PolicySets module — CRUD, prioritized policies, assignments (0.5.0)
- [x] RadiusAttributeGroups module — CRUD, reference data (0.5.0)
- [x] ExternalIdentities module — read-only query (0.5.0)
- [x] Venues unit identity methods — query, associate, remove (0.5.0)
- [x] client.request() files parameter for multipart uploads (0.5.0)
- [x] Deprecation header detection (0.5.0)

## Requested Features

_None yet._

## Future Modules

These R1 API tag groups have zero SDK coverage:

- MSP Services (93 ops)
- View Model Resources (89 ops)
- RUCKUS Edge (51 ops)
- Guest Service (32 ops)
- Workflow Service (28 ops)
- Property Management (27 ops)
- Entitlements (21 ops)
- Resident Portal (16 ops)
- Events and Alarms (10 ops)
- Pending Assets Management (10 ops)
- Workflow Actions (10 ops)
- Message Templates (8 ops)
- Client Management (6 ops)
- Activities (4 ops)
- Admin Enrollment (4 ops)
- Policy Evaluation (2 ops)
