<p align="center">
<img width="144" height="144" src="https://img.icons8.com/pulsar-gradient/144/tree.png" alt="tree"/>
</p>

<h1 align="center">Sylva identity discovery</h1>

<p align="center">
Note that Sylva is undergoing rapid development and documentation may be quickly obseleted and/or incomplete.
</p>

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
| [__Sherlock__][sherlock] | Sherlock extended for discovery of additional identities and branching
| Voter Records | Geographical, relation, and age lookup in 18 US States |


### Helpers and utilities

| Name | Description |
| --- | --- |
| [__FlareSolverr__][flaresolverr] | Proxy server to add support for additional target types |


## Usage

`sylva search <query>` will search all available modules for the given query.

`sylva branch <query>` will search all available modules for the given query, merge and deduplicate results, and resume searching with the newly found identities up to a certain depth. Some modules, particularly those with low API limits, may be branch disabled by default.

`sylva config --edit` to edit the configuration file (including API keys).

## Installation

Docker is the preferred method of installation, providing the most consistent experience.

```bash
docker run --rm ppfeister/sylva sylva search <query>
```

Other installation methods are described on the [__Sylva Wiki__][wiki-install].

### Packagers

It's recommended that you don't package Sylva yet. Changes are happening at rates quicker than most release cycles allow. If you'd like to package Sylva, feel free to reach out for info!

## Contributing

Contributors should refer to our [contributing guidelines][wiki-contributing] for information on how to contribute to the project. Note that since the project is still in its infancy, there isn't yet a formal roadmap.

Contributors opening a pull request are assumed to have read and agreed to the guidelines.

[wiki-install]: https://sylva.pfeister.dev/install/
[wiki-contributing]: https://sylva.pfeister.dev/contributing/introduction/

[sherlock]: https://github.com/sherlock-project/sherlock
[flaresolverr]: https://github.com/flaresolverr/flaresolverr

[xorg-x11-server-Xvfb]: https://packages.fedoraproject.org/pkgs/xorg-x11-server/xorg-x11-server-Xvfb/
