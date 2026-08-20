# Change History

## [0.7] - 2026-08-18

### Added
- `lib/` — offline Python wheels for all dependencies (Python 3.6, linux_x86_64), enables air-gapped deployment
- `run_*.py` — version check at top of each script (Python 3.4 gives clear error message)
- `run_*.py` — `ensure_deps()` auto-installs from `lib/` if present, falls back to PyPI

### Fixed
- `run_nrf.py` — removed duplicate `import sys`, removed `reload=True`
- `run_amf.py` — removed duplicate `import sys`, fixed undefined `logger` reference
- `run_udm.py` — removed duplicate `import sys`
- `run_web.py` — removed duplicate `import sys`
- All `run_*.py` — replaced f-strings in print statements with `.format()` for consistency

### Changed
- `requirements.txt` — pinned to Python 3.6 compatible versions (fastapi==0.63.0, uvicorn==0.13.4, pydantic==1.7.4, etc.)

---

## [0.6] - 2026-08-18

### Added
- `nrf/main.py` — `PUT /nnrf-nfm/v1/nf-instances/{nfInstanceId}` (standard 3GPP registration/update)
- `nrf/main.py` — `DELETE /nnrf-nfm/v1/nf-instances/{nfInstanceId}` (deregistration)
- `nrf/main.py` — `registrationTime` auto-recorded on first registration
- `nrf/models.py` — NFType extended: NRF, SMF, PCF, AUSF, UPF, NEF, NSSF, BSF, CHF, SCP, SEPP, OTHER
- `nrf/models.py` — `services` and `status` now have default values; `registrationTime` field added
- `web/main.py` — `GET /api/nrf/instances` proxy endpoint
- `web/main.py` — `GET /api/logs` endpoint; subprocess stdout streamed to in-memory ring buffer (200 lines)
- `web/main.py` — background thread reads stdout of each started service process
- `web/static/index.html` — NRF Registry page: table showing all registered NFs with type, instance ID, address, FQDN, services, status, registration time
- `web/static/index.html` — Event log auto-fetches `/api/logs` every 3s, shows service process output with color coding
- `amf/config.py`, `udm/config.py` — `nrf_host`/`nrf_port` override fields (per-service NRF address)
- `web/static/index.html` — AMF and UDM config pages each have NRF override address fields
- `web/config_store.py` — `amf.nrf_host`, `amf.nrf_port`, `udm.nrf_host`, `udm.nrf_port` default fields

### Changed
- `nrf/main.py` — registry changed from list to dict (keyed by nfInstanceId)
- `amf/main.py` — NRF registration changed from POST to PUT; `register_to_nrf` returns bool
- `udm/main.py` — NRF registration changed from POST to PUT; `wait_and_register` now loops forever (NRF restart recovery); registered all three services (uecm/ueau/sdm)
- `udm/api/uecm.py` — requested MSISDN/IMEI echoed back in response; other identities from static config; AMF instance ID now read from `amf.instance_id` instead of `static_data`
- `web/static/index.html` — removed all emoji from UI (nav icons, headers, buttons)
- `saveAmfAndLmf()` — now includes `nrf_host`/`nrf_port` fields
- `saveSection()` — `parseInt` NaN now stored as 0 instead of null
- `amf/config.py`, `udm/config.py` — NRF port override uses explicit `if` check instead of `or` (avoids port=0 false fallback)
- `nrf/main.py`, `amf/session.py` — removed Python 3.9+ built-in generic type annotations (`dict[...]`)
- `amf/api/namf_comm.py` — `dict | None` replaced with `Optional[dict]` for Python 3.6 compatibility

---

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
