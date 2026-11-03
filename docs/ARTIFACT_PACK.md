# Context Artifact Pack

The artifact pack is a complete folder of files designed for handoff, AI review, and project understanding.

## Files

- `CONTEXT.md` - the main AI-ready context bundle
- `context-manifest.json` - machine-readable metadata
- `context-manifest.md` - human-readable manifest
- `context-index.md` - selected files grouped by language
- `context-outline.md` - extracted source and documentation outline
- `context-insights.md` - practical context quality insights
- `context-audit.md` - safety and sharing-risk report

## Command

```bash
contextpack pack . --output-dir contextpack-artifacts --zip contextpack-artifacts.zip
```
