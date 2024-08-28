![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ppfeister/sylva/regression.yaml?branch=master&event=release&style=for-the-badge&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAABEklEQVR4nO2ZSw7CMAwFfWuW6bK3HsQCCUFaxf3Q2n6zRbV4IyuxWzMhhBD/B5iA2QqHfzNXDl9LAv3wNSSwHj63BMbC55SAL3wuCWwLn0MC+8LHloA/fAMeKSSwIfzHs7ElsCN8eAkceNqHk8AJp30oCSz/WUlwoE5AEtyd8HOLVDoTmiUfhaeVut3fbgXaBVxoFwg3/PTQLlBx+HmhXQDtAiYJJglXdMI9x2G0C5h2AbQLuNAuEHIC/Ea7gI/FKyxcJ3DAF6HQEvDd+8PDS0YJ7cC64SS0E+qGkdDuWvcURt/fL7XK3rq3gIH3914Bo3XDwAYBqUAC+lgVkIA+VgUkoI9VAQnoY1WgugAhhLCLeQK0o/Lg9gzSKwAAAABJRU5ErkJggg==&label=Release)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ppfeister/sylva/regression.yaml?branch=master&style=for-the-badge&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAABEklEQVR4nO2ZSw7CMAwFfWuW6bK3HsQCCUFaxf3Q2n6zRbV4IyuxWzMhhBD/B5iA2QqHfzNXDl9LAv3wNSSwHj63BMbC55SAL3wuCWwLn0MC+8LHloA/fAMeKSSwIfzHs7ElsCN8eAkceNqHk8AJp30oCSz/WUlwoE5AEtyd8HOLVDoTmiUfhaeVut3fbgXaBVxoFwg3/PTQLlBx+HmhXQDtAiYJJglXdMI9x2G0C5h2AbQLuNAuEHIC/Ea7gI/FKyxcJ3DAF6HQEvDd+8PDS0YJ7cC64SS0E+qGkdDuWvcURt/fL7XK3rq3gIH3914Bo3XDwAYBqUAC+lgVkIA+VgUkoI9VAQnoY1WgugAhhLCLeQK0o/Lg9gzSKwAAAABJRU5ErkJggg==&label=Head)



Since projects like these contain many moving parts, we prefer to use regression testing to ensure that changes don't break existing functionality. Regression testing is built into our CI (build statuses are shown above), with tests occuring on both changes to `master` and the publication of new releases before their builds are pushed for distribution.

Note that it's normal for the build status of `master` (at the HEAD of the branch) to be failing on occasion, due to the staged application of certain changes. **Most of the time** our CI will prevent these failed builds from replacing `preview` images, but we may override that on occasion.

Contributors __SHOULD__ run the test suite locally before committing changes, to ensure that all bases are covered. The test suite can be fully self-contained in the pdm development environment, and can therefore be ran without any additional local dependencies.

## Running unit tests

Contributors that have installed the development environment via `pdm install -G:all` as described in the [Advanced Install][advanced-install]{target="_blank"} guide can run the test suite one of two ways:

#### Within venv

```bash
tox p
```

#### Outside of venv

```bash
pdm run tox p
```

[advanced-install]: /install-adv/#installing-sylva-for-development
