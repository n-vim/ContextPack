# Architecture

ContextPack is organized into small modules.

- `scanner.py` selects files from a repository.
- `filters.py` decides what should be included or skipped.
- `bundler.py` renders the final context bundle.
- `profiles.py` applies workflow-specific settings.
- `splitter.py` creates token-limited chunks.
- `manifest.py` creates machine-readable bundle metadata.
- `insights.py` explains practical next steps.
