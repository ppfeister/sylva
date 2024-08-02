# Sylva - Identity discovery made easy

Sylva is undergoing rapid development. Documentation may be quickly obseleted and/or incomplete.

## Summary

### Useful Integrations

| Name | Description | API Key |
| --- | --- | --- |
| Endato | Person data source (phone, address, cell, etc) | Req [ T \| $ ] |
| ~~IntelX~~ | ~~Data leak source~~ | ~~Req [ T \| $ ]~~ |
| ProxyNova | COMB API (cleartext passwords, usernames) | Native |
| Veriphone | Phone number lookup | Req [ F+ ] |
| GitHub | See detail below | Opt [ F ] |

$ : paid | T : trial | F : Free | F+ : Freemium

Most development was done without any paid access -- so despite some integrations requiring an account, the full experience can be attained without any subscriptions.

#### GitHub Integration

Query GitHub for any known PGP keys, scrape both the oldest and newest 1000 commit authorships (2000 total) for leaked identifying information, and search for identities based on full name, email, or username.

Personal Access Token (PAT) is requried for PGP scraping, but all other functions work out of the box. PAT is _recommended_ for higher rate limits on other functions. PAT does not require any permissions assigned to it whatsoever.

### Native modules

| Name | Description |
| --- | --- |
| PGP Search | Search for identities through discovered PGP keys |
| [__Sherlock__][sherlock] | Sherlock extended for discovery of additional identities and spidering
| Voter Records | Geographical, relation, and age lookup in 18 US States |


### Helpers and utilities

| Name | Description |
| --- | --- |
| [__FlareSolverr__][flaresolverr] | Proxy server to add support for additional target types |

> [!NOTE]
> FlareSolverr is packaged with Sylva by default, but it bears two dependencies that may require manual installation. Automating this process is on my todo list. __Many users already have both of these installed.__
> - [xorg-x11-server-Xvfb][xorg-x11-server-Xvfb] or your distribution's equivalent
> - Either Chome or Chromium (used headlessly to solve captchas)


## Usage

`sylva search <query>` will search all available modules for the given query.

`sylva spider <query>` will search all available modules for the given query, merge and deduplicate results, and resume searching with the newly found identities up to a certain depth. Some modules, particularly those with low API limits, may be spider disabled by default.

`sylva config --edit` to edit the configuration file (including API keys).

## Installation

> [!TIP]
> Users who prefer `pip` over `pipx` can simply substitute the command for PyPI.

| Method | Command | Officially supported |
| --- | --- | --- |
| PyPI | `pipx install sylva` | ✅ |

### Packagers

It's recommended that you don't package Sylva yet. Changes are happening at rates quicker than most release cycles allow. If you'd like to package Sylva, feel free to reach out for info!

## Contributing

Contributors should refer to our [contributing guidelines][contributing] for information on how to contribute to the project. Note that since the project is still in its infancy, there isn't yet a formal roadmap.

Contributors opening a pull request are assumed to have read and agreed.

[contributing]: CONTRIBUTING.md
[sherlock]: https://github.com/sherlock-project/sherlock
[flaresolverr]: https://github.com/flaresolverr/flaresolverr

[xorg-x11-server-Xvfb]: https://packages.fedoraproject.org/pkgs/xorg-x11-server/xorg-x11-server-Xvfb/
