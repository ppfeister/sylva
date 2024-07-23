# Oculus - OSINT Simplified

Oculus is undergoing rapid development. Documentation may be quickly obseleted and/or incomplete.

## Summary

### Integrations

| Name | Description | API Key |
| --- | --- | --- |
| Endato | Person data source (phone, address, cell, etc) | Req [ T \| $ ] |
| ~~IntelX~~ | ~~Data leak source~~ | ~~Req [ T \| $ ]~~ |
| ProxyNova | COMB API (cleartext passwords, usernames) | Native |
| Veriphone | Phone number lookup | Req [ F+ ] |
| GitHub | See detail below | Opt [ F ] |

$ : paid | T : trial | F : Free | F+ : Freemium

Most development was done without any paid access -- so despite some integrations requiring an account, the full experience can be attained by all without a subscription.

#### GitHub Integration

Query GitHub for any known PGP keys, and scrape both the oldest and most recently authored commits (up to 2000 commits total) for any leaked identifying information.

Personal Access Token (PAT) authentication is required for PGP scraping, but is __not__ required for commit scraping. If a PAT is provided, commit scraping will have a higher rate limit. PAT does not require any permissions whatsoever.

### Built-in modules

| Name | Description |
| --- | --- |
| PGP Spider | Query common keyservers for undiscovered uids |
| Sherlock (extended) | [__Sherlock__][sherlock] extended for discovery of additional identities and spidering

## Usage

`oculus search <query>` will search all available modules for the given query.

`oculus spider <query>` will search all available modules for the given query, merge and deduplicate results, and resume searching with the newly found identities up to a certain depth. Some modules, particularly those with low API limits, may be spider disabled by default.

`oculus config --edit` to edit the configuration file (including API keys).

## Installation

Oculus uses a pdm backend. Developers can run `pdm install` and source the venv for a live development and testing environment.

### Packagers

Do not package Oculus yet. Changes are happening at rates quicker than most release cycles allow, and they aren't readily tagged for consistent feature sets. Depending on availability, name changes are also very possible at this stage.

Contact for information about planned packaging.

Once ready for production, Oculus will adopt properly tagged releases for consistent downstream packaging.

## Contributing

Contributors should refer to our [contributing guidelines][contributing] for information on how to contribute to the project. Note that since the project is still in its infancy, there isn't yet a formal roadmap.

Contributors opening a pull request are assumed to have read and agreed.

[contributing]: CONTRIBUTING.md
[sherlock]: https://github.com/sherlock-project/sherlock
