# PubMed QA Benchmark — Running Instructions

## Prerequisites

### Python 3.10+

```bash
# Linux / macOS
python3 --version
```
```cmd
:: Windows
python --version
```

Download from [python.org](https://www.python.org/downloads/) if not installed.

---

Dependencies can be installed directly into the system Python (Section 1) or into an isolated virtual environment (Section 2). Virtual environments keep project dependencies separate from the rest of the system and from each other, preventing conflicts — this is the recommended approach.

---

## 1. Global Installation

> Installs packages into the system Python. Not recommended — packages may conflict with other projects over time.

**Linux / macOS**

> **Linux:** pip is not bundled with the system Python on most distributions. Install it first:
> ```bash
> sudo apt install python3-pip   # Ubuntu / Debian
> sudo dnf install python3-pip   # Fedora
> ```

```bash
pip3 install -r requirements.txt
python3 main.py <SMABBLER_API_KEY>
```

**Windows**

```cmd
pip install -r requirements.txt
python main.py <SMABBLER_API_KEY>
```

---

## 2. Virtual Environments (recommended)

A virtual environment is an isolated Python installation with its own set of packages, separate from the system. With Python's built-in venv (2.1), you activate the environment in your shell before each use and deactivate it when done. uv (2.2) creates and manages the environment automatically — `uv run` handles activation implicitly, so no manual step is needed. Choose one of the following approaches.

### 2.1 Python venv

`venv` is included with Python on Windows and macOS. On Linux it may require a separate installation:

```bash
sudo apt install python3-venv   # Ubuntu / Debian
# Fedora: no extra step needed
```

**Linux / macOS**

First time:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py <SMABBLER_API_KEY>
deactivate
```

> **Fish shell:** replace `source .venv/bin/activate` with `source .venv/bin/activate.fish`

Every subsequent run (environment and packages already in place):

```bash
source .venv/bin/activate
python main.py <SMABBLER_API_KEY>
deactivate
```

**Windows (cmd)**

First time:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python main.py <SMABBLER_API_KEY>
deactivate
```

Every subsequent run:

```cmd
.venv\Scripts\activate.bat
python main.py <SMABBLER_API_KEY>
deactivate
```

**Windows (PowerShell)**

First time:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py <SMABBLER_API_KEY>
deactivate
```

Every subsequent run:

```powershell
.venv\Scripts\Activate.ps1
python main.py <SMABBLER_API_KEY>
deactivate
```

> **PowerShell execution policy:** if activation fails, run this command once first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 2.2 uv (Astral)

Install uv if not already available:

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```
```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
```cmd
:: Windows (cmd) — via MSI
msiexec /i https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.msi
```

`pyproject.toml` contains the full dependency configuration. The following commands are **identical on all platforms and shells**:

```
uv sync
uv run python main.py <SMABBLER_API_KEY>
```

`uv sync` resolves dependencies and sets up the environment on first run. On subsequent runs it is not needed:

```
uv run python main.py <SMABBLER_API_KEY>
```
