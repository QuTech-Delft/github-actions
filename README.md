# GitHub-Actions

Repository containing reusable workflows for the QuTech organisation.

## Installation

The reusable workflows from this repository can be referenced by "using" them in your GitHub actions workflow. No need
to install any packages for this.

Note that these are not completely generic actions, and will only be of use when a GitHub repository conforms to the standards for QI projects on GitHub, which is to say, it uses the following tools:

- Tox for running dev tools with the following environments:
  - `lint` for running linters and formatters
  - `type` for running type checkers
  - `docs` for building documentation
  - `test` for running unt tests
- Poetry for project/package management

An example of such a set-up can be found in [Qiskit-QI](https://github.com/QuTech-Delft/qiskit-quantuminspire).

## Usage

Using a workflow:

```yaml
jobs:
  run-poetry-tests:
    uses: qutech-delft/github-actions/.github/workflows/poetry_tests.yaml
    with:
      python-version: "3.11"
    secrets:
      github_token: ${{ secrets.GITHUB_TOKEN }}
```

Using an action:

```yaml
jobs:
  deploy-preview:
    runs-on: "ubuntu-latest"
    steps:
      - uses: QuTech-Delft/GitHub-Actions/actions/docs/sphinx-docs-preview@master
```

Additional information can be found: <https://docs.github.com/en/actions/sharing-automations/reusing-workflows>

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[Apache](http://www.apache.org/licenses/)
