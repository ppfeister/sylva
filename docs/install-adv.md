# Installing Sylva the hard way

Installing Sylva from source has __zero__ official support for end users. We only
recommend this method for advanced users or those who plan to contribute to the
project.

For the purposes of this document, it is assumed that the user is running Linux.

## Overview

Sylva uses a [PDM]{:target="_blank"} backend. There is no `requirements.txt` file, and Issues should
__not__ be raised for this missing file.

## Prerequisites

- [Install PDM according to their documentation][pdm-install]{:target="_blank"}

## Installing Sylva for development

```bash
git clone https://github.com/ppfeister/sylva.git
cd sylva
pdm install -G:all
```

Sylva is now installed in an isolated live environment. Changes made to the code should be reflected
within this environment immediately.

All dependency groups are installed, including those for regression testing, MkDocs editing, etc.

#### Running within the venv

Users can enter the virtual environment by running `source .venv/bin/activate`. The difficulty here
is that global installs of the same package are known to interfere. If you have Sylva installed
globally as well, you should defer to the next method.

Assuming you have entered the venv, you can run Sylva as you would normally.

#### Running via PDM

Due to the aforementioned complication, many developers may opt to run Sylva through PDM itself.

```bash
pdm run sylva search <query>
```

## Installing Sylva globally

!!! warning
    This is __not__ an officially supported method of installation.
    
    This method also lacks any means of automatic or assisted updates.

```bash
git clone https://github.com/ppfeister/sylva.git
cd sylva
pdm install --global --prod
```


[PDM]: https://pdm-project.org
[pdm-install]: https://pdm-project.org/en/latest/#installation
