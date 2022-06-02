# Last tested on Windows 10, Python 3.10.4

# Getting started on Windows
- Requires Python 3.9
- Standard setup for python project
  - `python -m venv venv`
  - `.\venv\Scripts\activate`
  - `pip install -r requirements.txt`

## Running from Pycharm (recommended)
- Set `venv` virtualenv as the python interpreter.
- Run `app.py -e` to launch a dedicated console.
- Alternatively, run with `-e` to run the app in the IDE console output.
  - Make sure to enable "Emulate terminal in output console"
## Running from Windows console (cmd)
- Nothing special - this should just work
## Running from Windows Terminal
- Run "Windows Terminal" as administrator
- Run `Set-ExecutionPolicy Bypass`

# Getting started on MacOS
- Requires Python 3.9
- `python -m venv venv`
- comment out the pywin32 dependencies from requirements.txt (sorry)
- `. venv/bin/activate`
- `pip install -r requirements.txt`

## Running from Pycharm
- Select "emulate terminal in output console"
- Run app.py
- Sorry, I didn't get it properly working with a second launched console like I did with Windows

## Running from terminal
- Just run app.py
