# classio

IO tools for python classes. This package builds on
- [dummio]() for a standardized interface to diverse IO methods for different data structures
- [packio]() to facilitate serialization of multiple sub-objects into a single file


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
