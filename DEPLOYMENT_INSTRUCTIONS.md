# Deploying `opencap-visualizer` to PyPI

## Build (from repo root)

```bash
cd /path/to/opencap-visualizer-pip
python -m pip install build twine
rm -rf dist
python -m build
twine check dist/*
```

Expected artifacts for the current release:

- `dist/opencap_visualizer-<version>-py3-none-any.whl`
- `dist/opencap_visualizer-<version>.tar.gz`

Version is read from `opencap_visualizer.__version__` in `opencap_visualizer/__init__.py`.

## Upload to PyPI

Create an API token at [pypi.org → Account settings → API tokens](https://pypi.org/manage/account/) (scope: whole account or project `opencap-visualizer`).

**Option A — environment variables (recommended)**

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_TOKEN_HERE   # paste token; do not commit

twine upload dist/opencap_visualizer-1.4.1*
```

**Option B — one line**

```bash
twine upload dist/opencap_visualizer-1.4.1* \
  --username __token__ \
  --password pypi-YOUR_TOKEN_HERE
```

**TestPyPI (optional dry run)**

```bash
twine upload --repository testpypi dist/opencap_visualizer-1.4.1*
```

## After release

```bash
pip install --upgrade opencap-visualizer
pip install --upgrade "opencap-visualizer[live]"
opencap-visualizer --version
opencap-visualizer-stream --help   # entry point; run with a .json path
```

## Git tag (optional)

```bash
git tag v1.4.1
git push origin v1.4.1
```
