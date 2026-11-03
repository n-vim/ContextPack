# Commands

ContextPack provides commands for building, inspecting, auditing, and packaging AI-ready repository context.

## Build

```bash
contextpack build . --output CONTEXT.md
```

Options:

- `--prompt default|review|bugfix|docs|security`
- `--profile balanced|compact|deep|bugfix|docs|security`
- `--max-files 50`
- `--manifest`
- `--index`
- `--force`

## Inspect and summarize

```bash
contextpack tree .
contextpack summarize .
contextpack inspect .
contextpack tokens .
contextpack detect .
```

## Reports

```bash
contextpack export . --format markdown --output context-report.md
contextpack export . --format json --output context-report.json
contextpack export . --format html --output context-report.html
contextpack export . --format insights --output context-insights.md
```

## Manifest, index, and outline

```bash
contextpack manifest . --format json --output context-manifest.json
contextpack index . --output context-index.md
contextpack outline . --output context-outline.md
```

## Split large context

```bash
contextpack split . --max-tokens 12000 --output-dir context-chunks
```

## Budget and audit

```bash
contextpack budget . --output context-budget.md
contextpack audit . --output context-audit.md
```

## Artifact pack

```bash
contextpack pack . --output-dir contextpack-artifacts --zip contextpack-artifacts.zip
```

## Profiles and workspace

```bash
contextpack profiles
contextpack profile compact
contextpack workspace .
```

## Config

```bash
contextpack init
contextpack config .
contextpack doctor .
```
