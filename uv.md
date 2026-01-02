# Python Package Structure and uv Management Skill

## Overview
This skill covers how to properly structure Python projects, fix common packaging issues, and work with the uv package manager.

## Key Concepts

### Python Package Structure
- Proper organization with src/ directory layout
- Use of __init__.py files to create proper packages
- Module import structure and relative imports
- Entry point configuration for console scripts

### Project Configuration
- pyproject.toml configuration for setuptools packages
- Console script setup with [project.scripts] section
- Package discovery with [tool.setuptools.packages.find]
- Dependency management for development and runtime

## Problem-Solving Approach
1. **Diagnosis**: Identify misconfigurations between package structure and configuration files
2. **Restructuring**: Move files to proper directories while maintaining functionality
3. **Configuration Verification**: Ensure pyproject.toml matches actual structure
4. **Testing**: Verify all functionality continues to work after changes
5. **Documentation**: Update documentation to reflect actual usage patterns

## Common Issues and Solutions

### Terminal Compatibility for Interactive Libraries
- Issue: Interactive libraries like questionary may not work in all terminals 
- Solution: Understand that this is a terminal limitation, not a code issue
- Workaround: Use alternative terminals or run in cmd.exe on Windows

### Console Script Import Errors
- Issue: ModuleNotFoundError when running console scripts
- Solution: Ensure package is properly installed and pyproject.toml is correctly configured
- Best Practice: Use consistent module path in [project.scripts] that matches package structure

### Testing After Refactoring
- Always run tests after structural changes to ensure functionality remains intact
- Use `uv run python -m pytest` to run tests in the uv-managed environment
- Verify both unit tests and integration points after changes

## Tools and Commands
- `uv sync` - Install dependencies as specified in pyproject.toml
- `uv run <command>` - Execute commands in the project environment
- `uv sync --all-extras` - Install all optional dependencies including dev dependencies
- `python -m pytest` - Run tests with pytest in the proper environment

## Best Practices
- Maintain consistent directory structure matching configuration files
- Always test console scripts after installation
- Keep documentation updated with structural changes
- Use relative imports within packages
- Structure packages to support both direct execution and console scripts