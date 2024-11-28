# GitHub-Actions

Repository containing reusable workflows for the QuTech organisation.

## Installation

The reusable workflows from this repository can be referenced by "using" them in your GitHub actions workflow. No need
to install any packages for this.

## Usage

```yaml
jobs:
  run-poetry-tests:
    uses: qutech-delft/github-actions/.github/workflows/_poetry_tests.yaml
    with:
      python-version: "3.11"
    secrets:
      github_token: ${{ secrets.GITHUB_TOKEN }}
```

Additional information can be found: <https://docs.github.com/en/actions/sharing-automations/reusing-workflows>

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[Apache](http://www.apache.org/licenses/)
