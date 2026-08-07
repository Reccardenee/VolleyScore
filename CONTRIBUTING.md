# Contributing to VolleyScore

First off, thank you for considering contributing to VolleyScore! It's people like you that make VolleyScore such a great tool.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for VolleyScore. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

- **Use a clear and descriptive title** for the issue to identify the problem.
- **Describe the exact steps which reproduce the problem** in as much detail as possible.
- **Provide specific examples** to demonstrate the steps.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for VolleyScore, including completely new features and minor improvements to existing functionality.

- **Use a clear and descriptive title** for the issue to identify the suggestion.
- **Provide a step-by-step description of the suggested enhancement** in as much detail as possible.
- **Explain why this enhancement would be useful** to most VolleyScore users.

### Pull Requests

The process described here has several goals:

- Maintain VolleyScore's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible VolleyScore

Please follow these steps to have your contribution considered by the maintainers:

1.  Follow all instructions in the template
2.  Follow the style guides
3.  After you submit your pull request, verify that all status checks are passing

## Styleguides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Python Styleguide

All Python code should follow [PEP 8](https://www.python.org/dev/peps/pep-0008/).

### HTML/CSS Styleguide

- Use consistent indentation (2 or 4 spaces)
- Keep CSS classes semantic and reusable

## Testing

Every change must keep both test suites green. They run automatically in CI (`test` job in `.github/workflows/build.yml`); run them locally before pushing.

### Unit / integration tests (pytest)

These start a real server process on an isolated port (8123). Your `config.json` and `logs/` are backed up and restored automatically, so they are safe to run with a live config.

```bash
pip install pytest requests
python -m pytest scorebug/tests -q
```

### End-to-end tests (Playwright)

These launch a headless Chromium browser, drive the real control panel, and assert that the overlays update live. The suite starts its own isolated server on port 8130 (config/logs under `e2e/.tmp`).

```bash
cd e2e
npm install
npx playwright install chromium
npx playwright test
```

On Windows PowerShell you may need to prefix npm/npx with `cmd /c`, e.g. `cmd /c "npx playwright test"`.

### Writing tests

- Add pytest cases in `scorebug/tests/test_server.py`; use the `clean_state` fixture for an isolated server state. The server honors `VOLLEYSCORE_CONFIG` / `VOLLEYSCORE_LOG_DIR` / `VOLLEYSCORE_PORT` environment variables for isolation.
- Add Playwright specs under `e2e/tests/`; call `page.request.post('/reset_config')` at the start of each test and use the helpers in `e2e/tests/helpers.js`. Keep `workers: 1` (tests share one live server).
- Never write `(await request.get('/current')).json().field` - `json()` is async, so `.field` would be read off the pending Promise. Await it instead (see `helpers.getState`).

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests.

* `bug` - Issues that are bugs.
* `enhancement` - Issues that are feature requests.
* `documentation` - Issues that are documentation improvements.
