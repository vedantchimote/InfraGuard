# InfraGuard Documentation

This directory contains all documentation for the InfraGuard project.

## Directory Structure

```
documentation/
├── README.md                    # This file
├── Infraguard-design.md        # Original design document
├── mint.json                   # Mintlify configuration
├── docs.json                   # Auto-generated Mintlify config
├── favicon.svg                 # Site favicon
├── introduction.mdx            # Getting started page
├── quickstart.mdx              # Quick start guide
├── installation.mdx            # Installation guide
│
├── logo/                       # Brand assets
│   ├── dark.svg               # Logo for dark mode
│   └── light.svg              # Logo for light mode
│
├── concepts/                   # Core concepts documentation
│   ├── overview.mdx
│   ├── architecture.mdx
│   ├── anomaly-detection.mdx
│   ├── forecasting.mdx
│   └── alerting.mdx
│
├── deployment/                 # Deployment guides
│   ├── docker.mdx
│   ├── kubernetes.mdx
│   └── configuration.mdx
│
├── integrations/               # Integration guides
│   ├── prometheus.mdx
│   ├── slack.mdx
│   ├── jira.mdx
│   └── grafana.mdx
│
├── api-reference/              # API documentation
│   ├── introduction.mdx
│   ├── collector.mdx
│   ├── detector.mdx
│   ├── forecaster.mdx
│   └── alerter.mdx
│
├── guides/                     # How-to guides
│   ├── getting-started.mdx
│   ├── training-models.mdx
│   ├── custom-metrics.mdx
│   ├── runbooks.mdx
│   └── troubleshooting.mdx
│
├── advanced/                   # Advanced topics
│   ├── property-testing.mdx
│   ├── performance-tuning.mdx
│   ├── security.mdx
│   └── monitoring.mdx
│
└── technical-docs/             # Technical documentation (Markdown)
    ├── API.md
    ├── ARCHITECTURE.md
    ├── DEPLOYMENT.md
    └── TESTING.md
```

## Documentation Types

### 1. Mintlify Documentation (Interactive)
All `.mdx` files are part of the Mintlify documentation site with:
- Interactive components (cards, accordions, tabs)
- Mermaid diagrams
- Code examples with syntax highlighting
- Cross-references and navigation

**View locally:**
```bash
cd documentation
mintlify dev
```

Then open http://localhost:3000

### 2. Technical Documentation (Markdown)
The `technical-docs/` directory contains traditional Markdown documentation:
- API.md - API reference
- ARCHITECTURE.md - System architecture with diagrams
- DEPLOYMENT.md - Deployment instructions
- TESTING.md - Testing strategy and guidelines

### 3. Design Document
`Infraguard-design.md` - Original comprehensive design specification

## Editing Documentation

### Mintlify Pages (.mdx)
Edit any `.mdx` file and the dev server will auto-reload:
```bash
cd documentation
mintlify dev
```

### Configuration
Edit `mint.json` to:
- Update navigation structure
- Change colors and branding
- Add/remove pages
- Configure integrations

## Deployment

### Deploy to Mintlify
```bash
cd documentation
mintlify deploy
```

### Self-Host
Build static site:
```bash
cd documentation
mintlify build
```

## Resources

- [Mintlify Documentation](https://mintlify.com/docs)
- [MDX Documentation](https://mdxjs.com/)
- [Mermaid Diagrams](https://mermaid.js.org/)

## Contributing

When adding new documentation:
1. Create `.mdx` file in appropriate directory
2. Add to `mint.json` navigation
3. Follow existing formatting and style
4. Include code examples and diagrams
5. Test locally with `mintlify dev`
