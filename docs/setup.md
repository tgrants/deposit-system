# Setup

A general guide for preparing the working environment.
See the READMEs in each component for component-specific instructions.

## Linux

These instructions assume you use a Debian-derived distribution.
[Here's a quick guide](https://ubuntu.com/tutorials/command-line-for-beginners) for the Linux command line.

### Version control

To do version control on linux, you need to install the git package `sudo apt install git`.
After that, you can clone the repository `git clone https://github.com/tgrants/deposit-system`.

Additionally, consider setting up [GitHUb CLI](https://github.com/cli/cli) to contribute.
- Install Github `sudo apt install gh`
- Authenticate `gh auth login`

### Python

Python should come preinstalled on most distributions.
Run `python3 --version` to check the version and install it if necessary `sudo apt install python3`.

#### Virtual environment

Virtual environments are used to ensure that dependencies are managed and isolated from the system-wide Python packages.
This avoids potential conflicts between packages required by different projects.

Make sure the virtual environment packages are installed `python3-venv`.
Create it in the desired directory `python3 -m venv venv`.

Once the virtual environment is created, you need to activate it before installing any dependencies `source venv/bin/activate`.
Your shell prompt will change, indicating that you're now working within the environment.
For example, you might see (venv) before your command prompt.
Using one virtual environment for the whole project should be fine.

#### Dependencies

All dependencies are listed in the `requirements.txt` file. To install them, use `pip install -r requirements.txt`.
When you're done, you can deactivate the virtual environment using `deactivate`.

#### Interpreter

If you are using VSCode, the editor could show that some modules are missing, despite the code running just fine.
This is because your system and the virtual environment have differnet paths.

To solve this:
- Get interpreter path `which python` (while in venv)
- Set path `CTRL+SHIFT+P` -> `Python: Select interpreter`

#### Running

You can run the python code with `python3 path/to/program.py`.
Add options (flags) using dashes, for example `python3 controller/main.py -vw`.
The component READMEs should contain all available options and their descriptions.

## Windows

### Python

You can download python [here](https://www.python.org/downloads/windows/).
[Here's a good guide](https://www.digitalocean.com/community/tutorials/install-python-windows-10) for installing it on Windows 10.
Make sure you check the "Add python.exe to PATH" checkbox.

#### Dependencies

All dependencies are listed in the `requirements.txt` file. To install them, use `pip install -r requirements.txt`.

If you get a `Could not find module libzbar-64.dll` error, try installing [vcredist_x64.exe](https://www.microsoft.com/en-gb/download/details.aspx?id=40784).

## Next steps

See [development.md](./development.md) for the next steps.
