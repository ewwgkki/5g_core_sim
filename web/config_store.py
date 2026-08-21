# web/config_store.py

import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

DEFAULTS = {
    "tls": False,
    "log_level": "INFO",
    "web": {"host": "0.0.0.0", "port": 8080},
    "nrf": {"host": "127.0.0.1", "port": 8000},
    "amf": {
        "host": "127.0.0.1",
        "port": 9999,
        "fqdn": "fe-1.amf.5gc.mnc080.mcc240.3gppnetwork.org",
        "instance_id": "F63F4247-CC1F-46BC-A903-52184744F029",
        "mcc": "240",
        "mnc": "080",
        "locality": "",
        "amf_region_id": "FF",
        "amf_set_id": "001",
        "amf_id": "FF0001",
        "tac": "000001",
        "sst": 1,
        "sd": "000001",
        "nrf_host": "",
        "nrf_port": 0
    },
    "lmf": {"host": "127.0.0.1", "port": 9988},
    "gmlc": {"host": "", "port": 0},
    "udm": {
        "host": "127.0.0.1",
        "port": 5555,
        "instance_id": "66909D42-05FE-4F2B-98E2-55B7329A2B40",
        "fqdn": "udm.5gc.mnc080.mcc240.3gppnetwork.org",
        "mcc": "240",
        "mnc": "080",
        "routing_indicator": "0000",
        "supi_range_start": "240800000000000",
        "supi_range_end": "240809999999999",
        "gpsi_range_start": "46700000000",
        "gpsi_range_end": "46709999999",
        "nrf_host": "",
        "nrf_port": 0
    }
}

def load() -> dict:
    if not os.path.exists(CONFIG_PATH):
        save(DEFAULTS)
        return DEFAULTS
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    # merge with defaults to ensure all keys exist
    data.setdefault("tls", False)
    data.setdefault("log_level", "INFO")
    for section, values in DEFAULTS.items():
        if section in ("tls", "log_level"):
            continue
        if section not in data:
            data[section] = values
        else:
            for k, v in values.items():
                data[section].setdefault(k, v)
    return data

def save(config: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

def get_section(section: str) -> dict:
    return load().get(section, DEFAULTS.get(section, {}))
