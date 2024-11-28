# classio

IO tools for python classes, [on pypi](https://pypi.org/project/classio/), so `pip install classio`.

This project makes it as easy as possible to set up IO methods while following these principles:
- Cross-platform/version compatibility matters -> avoid pickle.
- A single file is simpler to manage than a directory -> 1-1 relationship between classes and files. We use [packio](https://github.com/zkurtz/packio) to achieve this.
- Users should not need to waste time writing boilerplate IO methods -> we rely on [dummio](https://github.com/zkurtz/dummio) for a standardized interface to numerous IO methods.


## Development

Create and activate a virtual env for dev ops:
```
git clone git@github.com:zkurtz/classio.git
cd classio
pip install uv
uv sync
source .venv/bin/activate
pre-commit install
```
