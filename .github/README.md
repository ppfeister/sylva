<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" width="100" height="100" srcset="../docs/assets/logo-white.png">
  <source media="(prefers-color-scheme: light)" width="100" height="100" srcset="../docs/assets/logo-black.png">
  <img alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="../docs/assets/logo-black.png">
</picture>
</p>

<h1 align="center">Sylva identity discovery</h1>

<p align="center">
<a href="https://codeclimate.com/github/ppfeister/sylva/maintainability"><img src="https://api.codeclimate.com/v1/badges/4884eb85ac21a8426edc/maintainability" /></a>
&nbsp; <a href="https://codeclimate.com/github/ppfeister/sylva/test_coverage"><img src="https://api.codeclimate.com/v1/badges/4884eb85ac21a8426edc/test_coverage" /></a>
&nbsp; <a href="#"><img alt="Static Badge" src="https://img.shields.io/badge/type%20safety-mypy-1868ff"></a>
</p>

<p align="center">
Note that Sylva is undergoing rapid development and documentation may be quickly obsoleted. Now that development has a consistent "direction", regression testing is being gradually introduced.
</p>
<p align="center">
Visit the <strong><a href="https://sylva.pfeister.dev">Sylva Wiki</a></strong> for more information.
</p>

## Summary

### Useful integrations and data sources

| Name | Description | API Key |
| --- | --- | --- |
| Endato | Person data source (phone, address, cell, etc) | Req [ T \| $ ] |
| ~~IntelX~~ | ~~Data leak source~~ | ~~Req [ T \| $ ]~~ |
| ProxyNova | COMB API (cleartext passwords, usernames) | Native |
| Veriphone | Phone number lookup | Req [ F+ ] |
| GitHub | See detail below | Opt [ F ] |
| Reddit | Natural language processing for residency hints  | Native |

$ : paid | T : trial | F : Free | F+ : Freemium

Most development was done without any paid access -- so despite some integrations requiring an account, the full experience can be attained without any subscriptions.

### Generic modules

| Name | Description |
| --- | --- |
| PGP Search | Search for identities through discovered PGP keys |
| [__Sherlock__][sherlock] | Sherlock extended for discovery of additional identities and branching
| Voter Records | Geographical, relation, and age lookup in 18 US States |

___

#### GitHub Integration

Query GitHub for any known PGP keys, scrape both the oldest and newest 1000 commit authorships (2000 total) for leaked identifying information, and search for identities based on full name, email, or username.

Personal Access Token (PAT) is required for PGP scraping, but all other functions work out of the box. PAT is _recommended_ for higher rate limits on other functions. PAT does not require any permissions assigned to it whatsoever.


## Quick Start

Docker is the preferred method of installation, providing the most consistent and predictable user experience.

```bash
docker run -it sylva/sylva --help
```

For a preview of the latest changes, the `preview` tag may be used.

```bash
docker run -it sylva/sylva:preview --help
```

> [!TIP]
> Some users may opt to add an alias to their shell for ease of use.
>
> Adding `alias sd="docker run -it sylva/sylva"` to your ~/.bashrc or ~/.zshrc will allow you to simply type `sd branch user123` rather than the entire docker command. Add the `:preview` tag if necessary.

Other installation methods are described on the [__Sylva Wiki__][wiki-install].

### Packagers

It's recommended that you don't package Sylva yet. Changes are happening at rates quicker than most release cycles allow. If you'd like to package Sylva, feel free to reach out for info!

## Contributing

Contributors should refer to our [contributing guidelines][wiki-contributing] for information on how to contribute to the project. Note that since the project is still in its infancy, there isn't yet a formal roadmap.

Contributors opening a pull request are assumed to have read and agreed to the guidelines.


## Stargazers over time
[![Stargazers over time](https://starchart.cc/ppfeister/sylva.svg?variant=adaptive)](https://starchart.cc/ppfeister/sylva)


[wiki-install]: https://sylva.pfeister.dev/install/
[wiki-contributing]: https://sylva.pfeister.dev/contributing/introduction/

[sherlock]: https://github.com/sherlock-project/sherlock
[flaresolverr]: https://github.com/flaresolverr/flaresolverr

[xorg-x11-server-Xvfb]: https://packages.fedoraproject.org/pkgs/xorg-x11-server/xorg-x11-server-Xvfb/
