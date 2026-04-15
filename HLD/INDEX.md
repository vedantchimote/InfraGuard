# InfraGuard HLD - Quick Reference Index

## 🚀 Quick Links

- [📖 Complete README](README.md) - Full documentation
- [📊 Diagrams Summary](DIAGRAMS_SUMMARY.md) - Generation status and statistics
- [🏗️ Design Document](../documentation/Infraguard-design.md) - Detailed design specification

## 📁 Directory Structure

```
HLD/
├── README.md                                    # Complete documentation
├── DIAGRAMS_SUMMARY.md                          # Generation summary
├── INDEX.md                                     # This file
│
├── 01-system-architecture.puml                  # System overview
├── 02-component-interaction-sequence.puml       # Runtime behavior
├── 03-data-flow-architecture.puml               # Data transformations
├── 04-ml-pipeline-architecture.puml             # ML workflow
├── 05-alert-routing-flow.puml                   # Alert logic
├── 06-deployment-architecture-kubernetes.puml   # K8s deployment
├── 07-deployment-architecture-docker-compose.puml # Local dev
├── 08-class-diagram-core-components.puml        # Class structure
├── 09-forecasting-pipeline.puml                 # Forecasting workflow
├── 10-monitoring-and-observability.puml         # Observability
├── 11-security-architecture.puml                # Security controls
├── 12-error-handling-and-resilience.puml        # Resilience patterns
│
└── [Generated PNG files]                        # Rendered images
```

## 🎯 Find Diagrams by Purpose

### I want to understand...

#### ...the overall system
→ [01-system-architecture.puml](01-system-architecture.puml)

#### ...how components interact at runtime
→ [02-component-interaction-sequence.puml](02-component-interaction-sequence.puml)

#### ...how data flows through the system
→ [03-data-flow-architecture.puml](03-data-flow-architecture.puml)

#### ...how ML anomaly detection works
→ [04-ml-pipeline-architecture.puml](04-ml-pipeline-architecture.puml)

#### ...how alerts are routed
→ [05-alert-routing-flow.puml](05-alert-routing-flow.puml)

#### ...how to deploy to Kubernetes
→ [06-deployment-architecture-kubernetes.puml](06-deployment-architecture-kubernetes.puml)

#### ...how to run locally with Docker
→ [07-deployment-architecture-docker-compose.puml](07-deployment-architecture-docker-compose.puml)

#### ...the code structure and classes
→ [08-class-diagram-core-components.puml](08-class-diagram-core-components.puml)

#### ...how forecasting works
→ [09-forecasting-pipeline.puml](09-forecasting-pipeline.puml)

#### ...how the system is monitored
→ [10-monitoring-and-observability.puml](10-monitoring-and-observability.puml)

#### ...security controls
→ [11-security-architecture.puml](11-security-architecture.puml)

#### ...error handling and resilience
→ [12-error-handling-and-resilience.puml](12-error-handling-and-resilience.puml)

## 👥 Find Diagrams by Role

### Software Developer
1. [Class Diagram](08-class-diagram-core-components.puml) - Code structure
2. [Data Flow](03-data-flow-architecture.puml) - Data transformations
3. [ML Pipeline](04-ml-pipeline-architecture.puml) - ML implementation
4. [Component Interaction](02-component-interaction-sequence.puml) - Runtime behavior

### DevOps Engineer
1. [Kubernetes Deployment](06-deployment-architecture-kubernetes.puml) - Production setup
2. [Docker Compose](07-deployment-architecture-docker-compose.puml) - Local dev
3. [Monitoring](10-monitoring-and-observability.puml) - Observability
4. [Error Handling](12-error-handling-and-resilience.puml) - Resilience

### Security Engineer
1. [Security Architecture](11-security-architecture.puml) - Security controls
2. [Kubernetes Deployment](06-deployment-architecture-kubernetes.puml) - K8s security
3. [System Architecture](01-system-architecture.puml) - Attack surface

### Solution Architect
1. [System Architecture](01-system-architecture.puml) - Overall design
2. [Data Flow](03-data-flow-architecture.puml) - Data pipeline
3. [Deployment Options](06-deployment-architecture-kubernetes.puml) - Infrastructure
4. [Security](11-security-architecture.puml) - Security posture

### Product Manager
1. [System Architecture](01-system-architecture.puml) - Feature overview
2. [Component Interaction](02-component-interaction-sequence.puml) - User flow
3. [Alert Routing](05-alert-routing-flow.puml) - Alert delivery
4. [Forecasting](09-forecasting-pipeline.puml) - Predictive features

## 🔍 Find Diagrams by Technology

### Machine Learning
- [ML Pipeline Architecture](04-ml-pipeline-architecture.puml)
- [Forecasting Pipeline](09-forecasting-pipeline.puml)
- [Data Flow Architecture](03-data-flow-architecture.puml)

### Kubernetes
- [Kubernetes Deployment](06-deployment-architecture-kubernetes.puml)
- [Monitoring & Observability](10-monitoring-and-observability.puml)
- [Security Architecture](11-security-architecture.puml)

### Docker
- [Docker Compose Deployment](07-deployment-architecture-docker-compose.puml)
- [System Architecture](01-system-architecture.puml)

### Prometheus
- [System Architecture](01-system-architecture.puml)
- [Data Flow Architecture](03-data-flow-architecture.puml)
- [Monitoring & Observability](10-monitoring-and-observability.puml)

### Slack & Jira
- [Alert Routing Flow](05-alert-routing-flow.puml)
- [Component Interaction Sequence](02-component-interaction-sequence.puml)
- [System Architecture](01-system-architecture.puml)

### Python & scikit-learn
- [ML Pipeline Architecture](04-ml-pipeline-architecture.puml)
- [Class Diagram](08-class-diagram-core-components.puml)
- [Data Flow Architecture](03-data-flow-architecture.puml)

## 📖 Documentation Hierarchy

```
InfraGuard Documentation
│
├── README.md (Project root)
│   └── Quick start and overview
│
├── HLD/ (This directory)
│   ├── INDEX.md (This file)
│   ├── README.md (Complete HLD guide)
│   ├── DIAGRAMS_SUMMARY.md (Generation status)
│   └── *.puml (Diagram sources)
│
├── documentation/
│   ├── Infraguard-design.md (Detailed design)
│   ├── concepts/ (Conceptual docs)
│   ├── api-reference/ (API docs)
│   ├── deployment/ (Deployment guides)
│   ├── guides/ (How-to guides)
│   └── integrations/ (Integration docs)
│
└── tests/
    └── README.md (Testing documentation)
```

## 🛠️ Common Tasks

### View a Diagram
1. Open the `.png` file in any image viewer
2. Or open the `.puml` file in VS Code with PlantUML extension

### Edit a Diagram
1. Open the `.puml` file in a text editor
2. Modify the PlantUML code
3. Regenerate: `docker run --rm -v $(pwd)/HLD:/data plantuml/plantuml:latest -tpng /data/*.puml`

### Add a New Diagram
1. Create a new `.puml` file following the naming convention: `##-descriptive-name.puml`
2. Add PlantUML code
3. Generate PNG: `docker run --rm -v $(pwd)/HLD:/data plantuml/plantuml:latest -tpng /data/your-file.puml`
4. Update README.md and this INDEX.md

### Export to Different Format
```bash
# SVG (vector graphics)
docker run --rm -v $(pwd)/HLD:/data plantuml/plantuml:latest -tsvg /data/*.puml

# PDF
docker run --rm -v $(pwd)/HLD:/data plantuml/plantuml:latest -tpdf /data/*.puml

# ASCII art
docker run --rm -v $(pwd)/HLD:/data plantuml/plantuml:latest -ttxt /data/*.puml
```

## 📊 Diagram Statistics

| Category | Count | Files |
|----------|-------|-------|
| Architecture | 4 | 01, 03, 04, 08 |
| Deployment | 2 | 06, 07 |
| Process Flow | 3 | 02, 05, 09 |
| Operational | 3 | 10, 11, 12 |
| **Total** | **12** | **All** |

## 🎨 Diagram Themes

All diagrams use consistent styling:
- **Blue tones**: External systems and data flow
- **Yellow tones**: Collection and transformation layers
- **Purple tones**: Intelligence and ML layers
- **Green tones**: Alerting and success states
- **Pink tones**: Configuration and security
- **Red tones**: Errors and critical states

## 🔗 External Resources

- [PlantUML Official Site](https://plantuml.com/)
- [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
- [PlantUML Language Reference](https://plantuml.com/guide)
- [VS Code PlantUML Extension](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml)

## 📞 Support

For questions about these diagrams:
1. Check the [README.md](README.md) for detailed explanations
2. Review the [Design Document](../documentation/Infraguard-design.md)
3. Refer to the [Architecture Overview](../documentation/concepts/architecture.mdx)

---

**Last Updated**: April 12, 2026  
**Total Diagrams**: 12  
**Status**: ✅ Complete  
**Format**: PlantUML (.puml) + PNG (.png)
