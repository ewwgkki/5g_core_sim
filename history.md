ethlab55[GMPC24-ICP2501,db1]:/home/ewwgkki/5g_core_sim # python3.6 run_web.py
Bootstrapped pip from: pip-21.3.1-py3-none-any.whl
Installing dependencies from lib/ (offline)...
Looking in links: /home/ewwgkki/5g_core_sim/lib
Processing ./lib/fastapi-0.63.0-py3-none-any.whl
Processing ./lib/uvicorn-0.13.4-py3-none-any.whl
Processing ./lib/httpx-0.16.1-py3-none-any.whl
Processing ./lib/pydantic-1.7.4-py3-none-any.whl
Processing ./lib/starlette-0.13.6-py3-none-any.whl
Processing ./lib/anyio-1.4.0-py3-none-any.whl
Processing ./lib/h11-0.12.0-py3-none-any.whl
Processing ./lib/click-7.1.2-py2.py3-none-any.whl
Processing ./lib/sniffio-1.2.0-py3-none-any.whl
Processing ./lib/idna-3.10-py3-none-any.whl
Processing ./lib/certifi-2025.4.26-py3-none-any.whl
Processing ./lib/httpcore-0.12.3-py3-none-any.whl
Processing ./lib/rfc3986-1.5.0-py2.py3-none-any.whl
Processing ./lib/typing_extensions-4.1.1-py3-none-any.whl
Processing ./lib/dataclasses-0.8-py3-none-any.whl
Processing ./lib/async_generator-1.10-py3-none-any.whl
INFO: pip is looking at multiple versions of httpcore to determine which version is compatible with other requirements. This could take a while.
INFO: pip is looking at multiple versions of click to determine which version is compatible with other requirements. This could take a while.
INFO: pip is looking at multiple versions of h11 to determine which version is compatible with other requirements. This could take a while.
INFO: pip is looking at multiple versions of anyio to determine which version is compatible with other requirements. This could take a while.
INFO: pip is looking at multiple versions of starlette to determine which version is compatible with other requirements. This could take a while.
INFO: pip is looking at multiple versions of pydantic to determine which version is compatible with other requirements. This could take a while.
INFO: pip is looking at multiple versions of httpx to determine which version is compatible with other requirements. This could take a while.
INFO: pip is looking at multiple versions of uvicorn to determine which version is compatible with other requirements. This could take a while.
INFO: pip is looking at multiple versions of <Python from Requires-Python> to determine which version is compatible with other requirements. This could take a while.
INFO: pip is looking at multiple versions of fastapi to determine which version is compatible with other requirements. This could take a while.
ERROR: Could not find a version that satisfies the requirement contextvars>=2.1; python_version < "3.7" (from sniffio) (from versions: none)
ERROR: No matching distribution found for contextvars>=2.1; python_version < "3.7"
pip install failed with exit code 1
ethlab55[GMPC24-ICP2501,db1]:/home/ewwgkki/5g_core_sim # # Change History

## [0.8.1] - 2026-08-21

### Added
- `build.sh` — PyInstaller packaging script, produces standalone distribution
- `dist/5g_core_sim/start.sh` — Web Console launcher (background)
- `dist/5g_core_sim/start_all.sh` — Start NRF + AMF + UDM without Web Console
- `dist/5g_core_sim/start_nrf.sh` — Start NRF individually (optional host/port args)
- `dist/5g_core_sim/start_amf.sh` — Start AMF individually (optional host/port args)
- `dist/5g_core_sim/start_udm.sh` — Start UDM individually (optional host/port args)
- `dist/5g_core_sim/stop.sh` — Stop all services
- `web/static/index.html` — Transport config page: Log Level selector (DEBUG/INFO/WARNING/ERROR)
- `config.json` — `log_level` global field
- `amf/main.py`, `udm/main.py` — configurable log level from config.json

### Changed
- `web/main.py` — stop service now kills orphaned processes by port (handles Web Console restart)
- `nrf/main.py` — `registrationTime` uses local time instead of UTC
- `amf/main.py`, `udm/main.py` — httpx/httpcore INFO logs suppressed (NRF health check no longer floods event log)
- `web/static/index.html` — NRF Registry auto-loads when navigating to page (no manual Refresh needed)

### Fixed
- `web/static/index.html` — TLS toggle click not working (label/checkbox double-toggle event conflict)
- `web/main.py` — stop service fails for orphaned processes after Web Console restart (port still occupied)

---

## [0.8] - 2026-08-20

### Added
- `web/static/index.html` — Transport configuration page (independent TLS global toggle)
- `web/static/index.html` — NRF Registry table now shows PLMN, NF Info (GUAMI/TAC for AMF, SUPI/GPSI ranges for UDM), and full nfServices
- `amf/config.py` — AMF NF Profile fields: MCC, MNC, locality, amfRegionId, amfSetId, amfId, TAC, SST, SD
- `udm/config.py` — UDM NF Profile fields: FQDN, MCC, MNC, routingIndicator, supiRanges, gpsiRanges
- `web/static/index.html` — AMF config page: PLMN & amfInfo card (MCC, MNC, Region ID, Set ID, AMF ID, TAC, S-NSSAI)
- `web/static/index.html` — UDM config page: PLMN & Slice card, SUPI/GPSI Ranges card
- `lib/hyperframe-5.2.0-py2.py3-none-any.whl` — h2 dependency for Python 3.6
- `lib/hpack-3.0.0-py2.py3-none-any.whl` — h2 dependency for Python 3.6
- `lib/Hypercorn-0.5.4-py3-none-any.whl` — last Hypercorn version supporting Python 3.6 (HTTP/2 h2c)
- `lib/pytoml-0.1.21-py2.py3-none-any.whl` — Hypercorn 0.5.4 dependency
- `utils/bootstrap.py` — dependency check now imports `hypercorn.asyncio.serve` (catches broken installs)
- `utils/bootstrap.py` — legacy mode uses `--force-reinstall` to ensure patched whl is installed

### Changed
- `nrf/models.py` — NFInstance model extended: `ipv4Addresses`, `plmnList`, `sNssais`, `amfInfo`, `udmInfo`, `nfServices` (full 3GPP NF Profile)
- `nrf/models.py` — NFService model extended: `serviceInstanceId`, `scheme`, `nfServiceStatus`, `fqdn`, `ipEndPoints`, `versions`, `defaultNotificationSubscriptions`
- `nrf/models.py` — `ipv4Addr`, `port` now Optional (new format uses `ipv4Addresses` + `nfServices.ipEndPoints`)
- `amf/main.py` — `register_to_nrf()` payload: full 3GPP NF Profile with amfInfo, plmnList, sNssais, nfServices (namf-comm + namf-loc with ipEndPoints, versions, defaultNotificationSubscriptions)
- `udm/main.py` — `register_to_nrf()` payload: full 3GPP NF Profile with udmInfo (supiRanges, gpsiRanges, routingIndicators), plmnList, sNssais, nfServices
- `amf/main.py`, `udm/main.py` — replaced `lifespan` context manager with `@app.on_event("startup"/"shutdown")` (compatible with FastAPI 0.63.0 + Starlette 0.13.6)
- `web/static/index.html` — TLS toggle moved from NRF config page to independent Transport page
- `web/static/index.html` — TLS toggle redesigned as sliding switch (grey=off left, green=on right)
- `web/config_store.py` — `load()` skips non-dict items when merging defaults (fixes `tls: bool` crash)
- `web/main.py` — `update_config()` handles non-dict values (direct assignment instead of `.update()`)
- `requirements.txt` — Hypercorn pinned to 0.5.4, added hyperframe, hpack, pytoml for Python 3.6 compatibility

### Fixed
- `web/config_store.py` — `'bool' object has no attribute 'items'` crash when loading config with `tls` field
- `web/main.py` — `'bool' object has no attribute 'update'` crash when saving TLS config
- `amf/main.py`, `udm/main.py` — startup tasks (NRF registration, LMF monitor) not executing due to `lifespan` parameter being silently ignored by Starlette 0.13.6

---

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
