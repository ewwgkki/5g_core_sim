5G Core Network Simulator
=========================

Requirements:

1. AMF IP and port must be configurable. Default: 127.0.0.1:9999
2. On AMF service startup:
   - If NRF is running, AMF must register to NRF using instance ID: F63F4247-CC1F-46BC-A903-52184744F029
   - If NRF is not running, AMF must continuously monitor NRF status and register immediately once NRF comes up
3. AMF must support Namf and Nlmf interface messages as defined in 3GPP
4. AMF must support configurable LMF address and port
5. All service configurations managed via Web GUI, persisted to config.json


Project Structure:

project_root/
├── Readme.txt               <- This file
├── requirements.txt         <- Python dependencies
├── udm_requirements.txt     <- UDM-specific requirements
├── config.json              <- Unified config file (auto-generated, all services read from here)
├── run_nrf.py               <- Start NRF service
├── run_amf.py               <- Start AMF service
├── run_udm.py               <- Start UDM service
├── run_web.py               <- Start Web Console (default: 127.0.0.1:8080)
├── .vscode/
│   └── launch.json          <- VS Code debug configurations
├── amf/
│   ├── main.py
│   ├── config.py            <- Reads from config.json
│   └── api/
│       └── namf_loc.py
├── nrf/
│   ├── main.py
│   ├── config.py            <- Reads from config.json
│   └── models.py
├── udm/
│   ├── main.py
│   ├── config.py            <- Reads from config.json (fixed residual AMF/LMF variable bug)
│   └── api/
│       └── uecm.py
├── web/
│   ├── main.py              <- Backend API (config read/write + service start/stop + status)
│   ├── config_store.py      <- Unified config read/write module
│   └── static/
│       └── index.html       <- Web GUI single page
└── utils/
    └── path.py


Phase Status:

| Phase   | Description                                                        | Status      |
|---------|--------------------------------------------------------------------|-------------|
| Phase 1 | NRF registration mechanism                                         | Done        |
| Phase 2 | AMF module (startup registration, NRF monitoring, Namf/Nlmf, LMF) | Mostly done |
| Phase 3 | UDM module (API interfaces, static/simulated data)                 | Done        |
| Phase 4 | LMF module (optional)                                              | Not started |
| Phase 5 | Web control panel (config + service control + status monitoring)   | Done        |
| Phase 6 | Integration testing, full flow simulation                          | Not started |


Phase 1 - NRF Checklist:

  [x] POST /nnrf-nfm/v1/nf-instances  (register NF)
  [x] GET  /nnrf-nfm/v1/nf-instances  (query NF instances)
  [x] GET  /nnrf-disc/v1/nf-instances (NF discovery)
  [x] NFInstance data model (with FQDN and services fields)


Phase 2 - AMF Checklist:

  [x] Detect NRF on startup and register (with configurable instance ID)
  [x] Configurable AMF IP/Port, default 127.0.0.1:9999
  [x] Configurable FQDN, registered to NRF
  [x] Configurable LMF address/port (injected into provide-pos request logic)
  [x] NRF registration services field uses correct AMF service names (namf-comm, namf-loc)
  [x] POST /namf-loc/v1/{ueContextId}/provide-pos-info (NLg: GMLC -> AMF)
  [x] Forwards DetermineLocation to LMF with correct 3GPP TS 29.572 request fields (NLs: AMF -> LMF)
  [x] Real-time LMF status monitoring (monitor_lmf)
  [x] NRF monitor runs as infinite loop, auto re-registers if NRF restarts
  [ ] /nlmf-loc/... is a stub, not forwarding to real LMF                      (todo)
  [ ] NRF health check uses GET nf-instances, semantically inaccurate          (todo)


Phase 3 - UDM Checklist:

  [x] UDM registers to NRF on startup (with NRF monitoring)
  [x] GET /nudm-uecm/v1/msisdn-{number}/registrations/amf-3gpp-access
  [x] GET /nudm-uecm/v1/imei-{imei}/registrations/amf-3gpp-access
  [x] Returns XML format (compatible with GMLC interface)
  [x] GET /nudm-ueau/v1/{supi}/security-information (authentication-data)
  [x] GET /nudm-sdm/v1/{supi}/nssai (network slice subscription data)
  [x] GET /nudm-sdm/v1/{supi}/am-data (access and mobility subscription data)
  [x] GET /nudm-sdm/v1/{supi}/smf-select-data (SMF selection data)
  [x] UDM static data (IMEI, IMSI, AMF info) configurable via config.json


Phase 5 - Web GUI Checklist:

  [x] Dashboard: real-time NRF/AMF/UDM/LMF status (auto-refresh every 10s)
  [x] Dashboard: one-click start/stop for each service
  [x] Dashboard: event log panel
  [x] NRF config page: Host/Port
  [x] AMF config page: Host/Port/FQDN/Instance ID
  [x] AMF config page: LMF connection address
  [x] UDM config page: Host/Port/Instance ID
  [x] LMF config page: Host/Port (for AMF to use)
  [x] Config persisted to config.json
  [x] All service config.py files read from config.json


Pending (priority order):

  1. Fix AMF NRF monitor - remove max_attempts, make it an infinite loop
  2. Implement UDM /nudm-ueau and /nudm-sdm interfaces
  3. Implement real /nlmf-loc/... forwarding logic
  4. Phase 4: Implement LMF module
  5. Phase 6: Integration testing


How to Start:

  # Recommended: start Web Console and manage all services from the GUI
  python3 run_web.py
  # Open http://127.0.0.1:8080

  # Or start services individually
  python3 run_nrf.py
  python3 run_amf.py
  python3 run_udm.py
