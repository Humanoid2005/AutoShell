# AutoShell 👨 ⚙ 🤖

_Shell which understands humans_

## Introduction

Autoshell is a natural language interfacable CLI application which adds on to the capabilities of your terminal and can execute commands for your input queries.

## Features

The AutoShell has three modes of functionality:

- **Manual Mode**: In this mode the AutoShell behaves like a regular shell which runs the shell commands entered in it.
- **AI mode**: This mode shows the power of the _AutoShell_. It converts your english queries into executable shell commands which perform the actions specified by you in the query.
- **AI-Chat mode**: You can chat with AI to clarify queries on technical issues and detailed description on technical topics.

### Additional Features:

- **Autocomplete for commands**
- **Maintain command history**
- **Generates command logs and generates the logs in a text file**
- **User management through local database**

## File Structure

```bash
AutoShell/
├── autoshell/
│   ├── __init__.py     # Makes the directory a Python package
│   ├── scripts/
│   │   ├── __init__.py # Makes the scripts directory a subpackage
│   │   ├── ai.py       # Contains AI functionality
│   │   ├── db.py       # Handles database operations
│   │   ├── cli.py      # Core command-line interface implementation
│   │   └── macros.py   # Has macros to handle execution status
│   └── __main__.py     # Enables running your package as a module with python -m autoshell
├── autoshell-egg-info/ # contains build information
├── bin/
│   ├── autoshell       # Executable script that acts as a wrapper for application
├── dist/               # contains build results
├── pyproject.toml      # Primary configuration file for packaging autoshell
├── LICENSE             # License
├── README.md           # Project documentation (You are here!)
└── requirements.txt    # Required dependencies
```

## Installation

Clone the project

```bash
  git clone https://github.com/Humanoid2005/AutoShell.git
```

Go to the project directory

```bash
  cd AutoShell
```

Install autoshell using pip

```bash
  pip install dist/autoshell-0.1.0-py3-none-any.whl
```

Run the CLI application

```bash
  autoshell
```

## Run Locally (without installing the package)

Clone the project

```bash
  git clone https://github.com/Humanoid2005/AutoShell.git
```

Go to the project directory

```bash
  cd AutoShell
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Run the CLI application

```bash
  python3 -m autoshell
```

## Contributions

I welcome contributions! Feel free to fork the project and open a pull request for any improvements, bug fixes, or new features.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
