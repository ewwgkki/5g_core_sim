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
6. All services run HTTP/2 (h2c cleartext by default, h2 over TLS optional via global toggle)
7. Supports Python 3.6 (offline lib/ install) and Python 3.8+ (PyPI install)


Project Structure:

project_root/
├── README.md                <- This file
├── requirements.txt         <- Python 3.6 dependencies (offline, lib/)
├── requirements-modern.txt  <- Python 3.8+ dependencies (PyPI)
├── config.json              <- Unified config file (auto-generated, all services read from here)
├── run_nrf.py               <- Start NRF service
├── run_amf.py               <- Start AMF service
├── run_udm.py               <- Start UDM service
├── run_web.py               <- Start Web Console (default: 0.0.0.0:8080)
├── .vscode/
│   └── launch.json          <- VS Code debug configurations
├── amf/
│   ├── main.py              <- AMF app, full NF Profile registration (amfInfo, plmnList, nfServices)
│   ├── config.py            <- Reads from config.json (host, port, FQDN, MCC/MNC, GUAMI, TAC, S-NSSAI)
│   └── api/
│       ├── namf_loc.py
│       └── namf_comm.py
├── nrf/
│   ├── main.py
│   ├── config.py            <- Reads from config.json
│   └── models.py            <- Full 3GPP NFInstance model (ipv4Addresses, amfInfo, udmInfo, nfServices)
├── udm/
│   ├── main.py              <- UDM app, full NF Profile registration (udmInfo, plmnList, nfServices)
│   ├── config.py            <- Reads from config.json (host, port, FQDN, MCC/MNC, SUPI/GPSI ranges)
│   └── api/
│       ├── uecm.py
│       ├── ueau.py
│       └── sdm.py
├── web/
│   ├── main.py              <- Backend API (config read/write + service start/stop + status)
│   ├── config_store.py      <- Unified config read/write module
│   └── static/
│       └── index.html       <- Web GUI single page
├── utils/
│   ├── path.py
│   ├── serve.py             <- HTTP/2 server (Hypercorn h2c/h2)
│   ├── bootstrap.py         <- Auto-install dependencies on first run
│   └── contextvars_stub.py  <- Python 3.6 contextvars shim
└── lib/                     <- Offline wheels for Python 3.6 air-gapped deployment


Phase Status:

| Phase   | Description                                                        | Status      |
|---------|--------------------------------------------------------------------|-------------|
| Phase 1 | NRF registration mechanism                                         | Done        |
| Phase 2 | AMF module (startup registration, NRF monitoring, Namf/Nlmf, LMF) | Done        |
| Phase 3 | UDM module (API interfaces, static/simulated data)                 | Done        |
| Phase 4 | LMF module (optional)                                              | Not started |
| Phase 5 | Web control panel (config + service control + status monitoring)   | Done        |
| Phase 6 | Integration testing, full flow simulation                          | Not started |


Phase 1 - NRF Checklist:

  [x] PUT  /nnrf-nfm/v1/nf-instances/{nfInstanceId}  (register/update NF)
  [x] GET  /nnrf-nfm/v1/nf-instances  (query NF instances)
  [x] GET  /nnrf-disc/v1/nf-instances (NF discovery with target-nf-type filter)
  [x] DELETE /nnrf-nfm/v1/nf-instances/{nfInstanceId} (deregistration)
  [x] NFInstance model: full 3GPP NF Profile (ipv4Addresses, fqdn, plmnList, sNssais, amfInfo, udmInfo, nfServices)


Phase 2 - AMF Checklist:

  [x] Detect NRF on startup and register (with configurable instance ID)
  [x] Full 3GPP NF Profile: amfInfo (guamiList, taiList, amfRegionId, amfSetId), plmnList, sNssais
  [x] nfServices: namf-comm (with defaultNotificationSubscriptions), namf-loc (with ipEndPoints, versions)
  [x] Configurable AMF IP/Port, default 127.0.0.1:9999
  [x] Configurable FQDN, MCC/MNC, AMF ID, TAC, S-NSSAI SST/SD, locality
  [x] Configurable LMF address/port (injected into provide-pos request logic)
  [x] NRF registration services field uses correct AMF service names (namf-comm, namf-loc)
  [x] POST /namf-loc/v1/{ueContextId}/provide-pos-info (NLg: GMLC -> AMF)
  [x] Forwards DetermineLocation to LMF with correct 3GPP TS 29.572 request fields (NLs: AMF -> LMF)
  [x] Real-time LMF status monitoring (monitor_lmf)
  [x] NRF monitor runs as infinite loop, auto re-registers if NRF restarts
  [x] Async LPP session: AMF suspends GMLC request, simulates UE LPP responses
  [x] POST /namf-comm/v1/{ueContextId}/n1-n2-messages  (LMF -> AMF, Namf_Communication)
  [x] POST /namf-comm/v1/{ueContextId}/n1-message-notify
  [x] POST /namf-comm/v1/{ueContextId}/n2-info-notify
  [x] AMF -> GMLC NI-LR EventNotify (send_event_notify_to_gmlc)
  [x] GMLC address configurable via config.json and Web GUI
  [ ] NRPPa simulation (gNodeB SS-RSRP measurement response)                   (todo)


Phase 3 - UDM Checklist:

  [x] UDM registers to NRF on startup (with NRF monitoring)
  [x] Full 3GPP NF Profile: udmInfo (routingIndicators, supiRanges, gpsiRanges), plmnList, sNssais
  [x] nfServices: nudm-uecm, nudm-sdm, nudm-ueau (with ipEndPoints, versions, fqdn)
  [x] Configurable FQDN, MCC/MNC, routing indicator, SUPI/GPSI ranges
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
  [x] Transport config page: global TLS toggle (sliding switch, applies to all services)
  [x] NRF config page: Host/Port
  [x] AMF config page: Host/Port/FQDN/Instance ID/Locality
  [x] AMF config page: PLMN & amfInfo (MCC, MNC, Region ID, Set ID, AMF ID, TAC, S-NSSAI)
  [x] AMF config page: LMF connection address
  [x] UDM config page: Host/Port/FQDN/Instance ID
  [x] UDM config page: PLMN & Slice (MCC, MNC, Routing Indicator)
  [x] UDM config page: SUPI/GPSI Ranges
  [x] LMF config page: Host/Port (for AMF to use)
  [x] GMLC config page: Host/Port (for AMF EventNotify)
  [x] NRF Registry page: Type, Instance ID, Address, FQDN, PLMN, NF Info, Services, Status, Registered
  [x] Config persisted to config.json
  [x] All service config.py files read from config.json


Pending (priority order):

  1. Phase 4: Implement LMF module
  2. Phase 6: Integration testing
  3. NRPPa simulation in AMF (gNodeB measurement response)


How to Start:

  # Recommended: start Web Console and manage all services from the GUI
  python3 run_web.py
  # Open http://127.0.0.1:8080

  # Or start services individually
  python3 run_nrf.py
  python3 run_amf.py
  python3 run_udm.py

  # Python 3.6 (air-gapped server): dependencies auto-installed from lib/
  python3.6 run_web.py


Python Version Support:

  Python 3.6:  Hypercorn 0.5.4 (HTTP/2 h2c), offline install from lib/
  Python 3.8+: Hypercorn latest (HTTP/2 h2c/h2), install from PyPI
  All versions: auto-detected, no manual configuration needed
