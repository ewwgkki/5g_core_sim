# Change History

## [0.5] - 2026-08-18

### Fixed
- `amf/main.py` — NRF registration services field corrected from `Namf/Nlmf` to `namf-comm/namf-loc` (per 3GPP TS 29.518)
- `amf/main.py` — Removed incorrect `/nlmf/v1/location/{ue_id}` route (Nlmf is LMF's service, not AMF's)
- `amf/main.py` — UE context route corrected to `/namf-comm/v1/ue-contexts/{ueContextId}`
- `amf/api/namf_loc.py` — DetermineLocation request body aligned to 3GPP TS 29.572: added `ueContextId`, `servingNrCellId`, `lcsCorrelationId`, `amfId` fields
- `amf/api/namf_loc.py` — Added reference comments clarifying NLg (GMLC->AMF) and NLs (AMF->LMF) reference points

---

## [0.4] - 2026-08-18

### Added
- `udm/api/ueau.py` — `GET /nudm-ueau/v1/{supi}/security-information` (authentication data, 3GPP TS 29.503)
- `udm/api/sdm.py` — `GET /nudm-sdm/v1/{supi}/nssai`, `am-data`, `smf-select-data` (subscription data)
- UDM static data (IMEI, IMSI, AMF info, MCC/MNC) moved to `config.json` under `udm.static_data`

### Changed
- `udm/api/uecm.py` — now reads static data from `config.json` instead of hardcoded values
- `udm/main.py` — registered ueau and sdm routers

---

## [0.3] - 2026-08-18

### Added
- Web Console (`run_web.py`, `web/`) — single-page GUI for config management and service control
- `config.json` — unified config file, all services read from here on startup
- `web/config_store.py` — centralized config read/write module
- `web/static/index.html` — dashboard with real-time service status, event log, one-click start/stop
- Config pages for NRF, AMF, UDM, LMF in Web GUI
- `.vscode/launch.json` — VS Code debug configurations for all services

### Changed
- `nrf/config.py`, `amf/config.py`, `udm/config.py` — all now read from `config.json` instead of hardcoded values
- `udm/config.py` — removed residual `AMF_HOST` / `LMF_HOST` variables that did not belong here

### Removed
- `common/` — empty folder, no purpose
- `nrf_control.py` — superseded by Web Console service control
- `launch.json` (root) — moved to `.vscode/launch.json`

### Fixed
- `udm/config.py` residual AMF/LMF variable bug

---

## [0.2] - 2026-08-18

### Added
- UDM module (`udm/main.py`, `udm/config.py`, `udm/api/uecm.py`)
- UDM registers to NRF on startup with infinite retry loop
- `GET /nudm-uecm/v1/msisdn-{number}/registrations/amf-3gpp-access`
- `GET /nudm-uecm/v1/imei-{imei}/registrations/amf-3gpp-access`
- UDM returns XML response compatible with GMLC interface
- `run_udm.py` startup script

---

## [0.1] - 2026-08-18

### Added
- NRF module (`nrf/main.py`, `nrf/config.py`, `nrf/models.py`)
- `POST /nnrf-nfm/v1/nf-instances` — NF registration
- `GET  /nnrf-nfm/v1/nf-instances` — NF instance query
- `GET  /nnrf-disc/v1/nf-instances` — NF discovery
- NFInstance data model with FQDN and services fields
- AMF module (`amf/main.py`, `amf/config.py`, `amf/api/namf_loc.py`)
- AMF registers to NRF on startup, configurable instance ID
- Configurable AMF IP/Port (default 127.0.0.1:9999), FQDN, LMF address/port
- `POST /namf-loc/v1/{ueId}/provide-pos-info` with LMF forwarding and fallback
- Real-time LMF status monitoring (`monitor_lmf`)
- NRF registration includes Namf and Nlmf in services field
- `run_nrf.py`, `run_amf.py` startup scripts
- `utils/path.py` — sys.path helper

---

## Pending

- [ ] Implement LMF module (Phase 4)
- [ ] Implement real `/nlmf-loc/...` forwarding in AMF
- [ ] Phase 6: Integration testing
