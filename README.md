# llms-for-verified-programs
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Getting started

### Set up the Nagini server
This project depends on the Nagini. Follow the instructions [here](https://github.com/marcoeilers/nagini) to set up Nagini. 
> Note: Nagini requires Python 3.8, hence set it up in a separate virtual environment.

Nagini can be run in server mode using this command:
```bash
python3 -m nagini_translation.main a --server
```
However, a code change in `nagini_translation.main` is required so that the server doesn't crash on exceptions [todo: provide link to modified nagini_translation/main.py here].

The server by default listens on `"tcp://localhost:5555"`, which we've used in the client (`DEFAULT_CLIENT_SOCKET`).

### Set up this project
Create a `.env` file at the root level with the following content. `.gitignore` takes care not to commit this file to version control.
```conf
GPT_SECRET_KEY=sk-<your_api_key>
```
Create a virtual environment with Python 3.12 and install dependencies of the project:
```bash
virtualenv l4vp
soruce l4vp/bin/activate
cd <this_directory>
pip install -r requirements.txt
```

Run experiments in the jupyter notebook [experiments.ipynb](experiments.ipynb). Make sure the Nagini server is running