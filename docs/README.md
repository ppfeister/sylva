# Oculus - OSINT Simplified

Oculus is undergoing rapid development. Documentation may be quickly obseleted and/or incomplete.

## Summary

### Integrations

| Name | Description | API Key |
| --- | --- | --- |
| Endato | Person data source (phone, address, cell, etc) | Req [ $ ] |
| IntelX | Data leak source | Req [ T \| $ ] |
| ProxyNova | COMB API (cleartext passwords, usernames) | Native |

### Built-in modules

| Name | Description |
| --- | --- |
| PGP Spider | Query common keyservers for undiscovered uids |

## Usage

`oculus search <query>` will search all available modules for the given query.

`oculus spider <query>` will search all available modules for the given query, merge and deduplicate results, and resume searching with the newly found identities up to a certain depth. Some modules, particularly those with low API limits, may be spider disabled by default.

`oculus config --edit` to edit the configuration file (including API keys).

## Installation

Oculus uses a pdm backend. Developers can run `pdm install` and source the venv for a live development and testing environment.

### Packagers

Do not package Oculus yet. Changes are happening quicker than most release cycles, and they aren't readily tagged. Contact for information about planned packaging.

Once ready for production, Oculus will adopt properly tagged releases for consistent downstream packaging.
