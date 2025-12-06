# Installation Guide

## The Problem

When you're in a virtual environment, you **cannot** use the `--user` flag with pip. This causes the error:
```
ERROR: Can not perform a '--user' install. User site-packages are not visible in this virtualenv.
```

## Solution: Use the Correct Commands

### Option 1: Use Virtual Environment's Pip (Recommended)

```bash
# Activate the virtual environment first
source .venv/bin/activate

# Then install packages normally (NO --user flag)
pip install <package-name>

# Or install from requirements.txt
pip install -r requirements.txt
```

### Option 2: Use Direct Path to Venv Pip

```bash
# Without activating, use the full path
.venv/bin/pip install <package-name>
```

### Option 3: Use Python Module

```bash
# Using the venv's Python
.venv/bin/python -m pip install <package-name>

# Or system Python (if not using venv)
python3 -m pip install <package-name>
```

### Option 4: Use the Helper Script

I've created a helper script for you:

```bash
./install_package.sh <package-name>
```

Example:
```bash
./install_package.sh pygame
./install_package.sh numpy
```

## Common Commands

### Install a single package:
```bash
.venv/bin/pip install <package-name>
```

### Install from requirements.txt:
```bash
.venv/bin/pip install -r requirements.txt
```

### Upgrade a package:
```bash
.venv/bin/pip install --upgrade <package-name>
```

### Uninstall a package:
```bash
.venv/bin/pip uninstall <package-name>
```

## Important Notes

1. **Never use `--user` in a virtual environment** - it's not allowed and will cause errors
2. **Always use `.venv/bin/pip`** when not activated, or activate first with `source .venv/bin/activate`
3. **If you see `--user` in any command**, remove it when using a venv

## Quick Reference

```bash
# Activate venv (then you can use 'pip' directly)
source .venv/bin/activate

# Install package
pip install <package>

# Deactivate when done
deactivate
```

