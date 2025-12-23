# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This is a Claude Code Plugin project that provides a PDF table of contents extraction skill.

### Project Configuration
- `.claude-plugin/marketplace.json`: Plugin configuration file defining the skill metadata and structure
- `pdf-toc-extractor/`: A skill directory for PDF table of contents extraction

### Current Skills
- **pdf-toc-extractor**: Extracts hierarchical bookmarks/outlines from PDF documents

## Development Commands

### Testing a Skill
```bash
# Validate Python syntax in skill scripts
python pdf-toc-extractor/scripts/test_syntax.py
```

### Adding New Skills
1. Create a new skill directory at the root level
2. Follow the skill structure pattern:
   - `SKILL.md`: Skill documentation
   - `scripts/`: Executable code
   - `references/`: Documentation to be loaded for context
   - `assets/`: Templates or resources for output
3. Update `.claude-plugin/marketplace.json` to include the new skill path

## Architecture

### Skill Organization Pattern
Each skill directory contains:
- **SKILL.md**: Skill description, usage examples, and documentation
- **scripts/**: Python scripts and modules implementing the skill functionality
- **references/**: API documentation and detailed guides loaded into Claude's context
- **assets/**: Files used in outputs (templates, samples, etc.)

### Plugin Configuration
The `.claude-plugin/marketplace.json` defines:
- Plugin metadata (name, owner, version)
- Skill paths relative to the plugin root
- Plugin loading behavior (strict: false allows dynamic skill loading)

## Notes for Development
- Skills are self-contained in their directories
- Scripts in `scripts/` may be executed within Claude's context
- References in `references/` are loaded to provide context
- This project follows the Claude Code Plugin specification