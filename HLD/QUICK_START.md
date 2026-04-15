# InfraGuard HLD - Quick Start Guide

## 🎯 What's in This Directory?

This directory contains 12 comprehensive High-Level Design (HLD) diagrams for the InfraGuard AIOps platform, created using PlantUML.

## 📂 Files Overview

- **12 `.puml` files**: PlantUML source code (editable)
- **12 `.png` files**: Rendered diagram images (ready to view)
- **3 `.md` files**: Documentation (README, INDEX, DIAGRAMS_SUMMARY)

## 🚀 Quick Start (30 seconds)

### Option 1: View PNG Images (Easiest)
Just open any `.png` file in your image viewer. Done!

**Recommended viewing order:**
1. `InfraGuard System Architecture.png` - Start here
2. `InfraGuard Component Interaction Sequence.png` - See how it works
3. `InfraGuard Data Flow Architecture.png` - Understand data flow

### Option 2: View in VS Code
1. Install "PlantUML" extension
2. Open any `.puml` file
3. Press `Alt+D` to preview

### Option 3: View Online
1. Copy content of any `.puml` file
2. Go to http://www.plantuml.com/plantuml/uml/
3. Paste and view

## 📖 Documentation Files

| File | Purpose | When to Read |
|------|---------|--------------|
| [INDEX.md](INDEX.md) | Quick reference index | Finding specific diagrams |
| [README.md](README.md) | Complete documentation | Understanding all diagrams |
| [DIAGRAMS_SUMMARY.md](DIAGRAMS_SUMMARY.md) | Generation status | Checking what's available |
| [QUICK_START.md](QUICK_START.md) | This file | Getting started quickly |

## 🎨 The 12 Diagrams

### Core Architecture (Start Here)
1. **System Architecture** - Overall system design
2. **Component Interaction** - How components work together
3. **Data Flow** - How data moves through the system

### Machine Learning
4. **ML Pipeline** - Anomaly detection workflow
9. **Forecasting Pipeline** - Predictive analysis

### Deployment
6. **Kubernetes Deployment** - Production setup
7. **Docker Compose** - Local development

### Operations
5. **Alert Routing** - How alerts are sent
10. **Monitoring** - System observability
11. **Security** - Security controls
12. **Error Handling** - Resilience patterns

### Development
8. **Class Diagram** - Code structure

## 🎯 Choose Your Path

### I'm a Developer
Start with:
1. System Architecture (overview)
2. Class Diagram (code structure)
3. Data Flow (data transformations)
4. ML Pipeline (algorithm details)

### I'm a DevOps Engineer
Start with:
1. System Architecture (overview)
2. Kubernetes Deployment (production)
3. Docker Compose (local dev)
4. Monitoring (observability)

### I'm a Security Engineer
Start with:
1. System Architecture (attack surface)
2. Security Architecture (controls)
3. Kubernetes Deployment (K8s security)

### I'm an Architect
Start with:
1. System Architecture (overall design)
2. Data Flow (data pipeline)
3. Deployment options (infrastructure)
4. All operational diagrams

### I'm a Product Manager
Start with:
1. System Architecture (features)
2. Component Interaction (user flow)
3. Alert Routing (notifications)
4. Forecasting (predictive features)

## 🔧 Common Tasks

### Regenerate All Diagrams
```bash
docker run --rm -v $(pwd)/HLD:/data plantuml/plantuml:latest -tpng /data/*.puml
```

### Regenerate One Diagram
```bash
docker run --rm -v $(pwd)/HLD:/data plantuml/plantuml:latest -tpng /data/01-system-architecture.puml
```

### Generate SVG (Vector Graphics)
```bash
docker run --rm -v $(pwd)/HLD:/data plantuml/plantuml:latest -tsvg /data/*.puml
```

### Edit a Diagram
1. Open the `.puml` file in any text editor
2. Modify the PlantUML code
3. Regenerate using command above
4. View the new `.png` file

## 📊 Diagram Sizes

| Diagram | Complexity | Best For |
|---------|-----------|----------|
| System Architecture | Medium | Presentations |
| Component Interaction | High | Technical docs |
| Data Flow | Medium | Developer onboarding |
| ML Pipeline | Medium | ML team discussions |
| Alert Routing | Low | Process documentation |
| Kubernetes Deployment | High | DevOps planning |
| Docker Compose | Medium | Local setup |
| Class Diagram | Very High | Code reviews |
| Forecasting Pipeline | Low | Feature planning |
| Monitoring | High | Operations runbooks |
| Security | High | Security reviews |
| Error Handling | High | Reliability planning |

## 🎓 Learning Path

### Day 1: Understand the System
1. Read [System Architecture](01-system-architecture.puml)
2. Read [Component Interaction](02-component-interaction-sequence.puml)
3. Read [Data Flow](03-data-flow-architecture.puml)

### Day 2: Deep Dive into ML
1. Read [ML Pipeline](04-ml-pipeline-architecture.puml)
2. Read [Forecasting Pipeline](09-forecasting-pipeline.puml)
3. Review [Class Diagram](08-class-diagram-core-components.puml)

### Day 3: Deployment & Operations
1. Read [Kubernetes Deployment](06-deployment-architecture-kubernetes.puml)
2. Read [Docker Compose](07-deployment-architecture-docker-compose.puml)
3. Read [Monitoring](10-monitoring-and-observability.puml)

### Day 4: Production Readiness
1. Read [Security](11-security-architecture.puml)
2. Read [Error Handling](12-error-handling-and-resilience.puml)
3. Read [Alert Routing](05-alert-routing-flow.puml)

## 💡 Tips

1. **Start with PNG files** - Easiest way to view
2. **Use INDEX.md** - Quick reference to find diagrams
3. **Read README.md** - Comprehensive explanations
4. **Edit PUML files** - Easy to modify and version control
5. **Regenerate often** - Keep diagrams up to date

## 🔗 Quick Links

- [Complete README](README.md) - Full documentation
- [Quick Reference Index](INDEX.md) - Find diagrams by purpose
- [Generation Summary](DIAGRAMS_SUMMARY.md) - Status and statistics
- [Design Document](../documentation/Infraguard-design.md) - Detailed design
- [Project README](../README.md) - Project overview

## ❓ FAQ

**Q: Which diagram should I start with?**  
A: Start with "System Architecture" for an overview.

**Q: How do I edit diagrams?**  
A: Edit the `.puml` files in any text editor, then regenerate.

**Q: Can I use these in presentations?**  
A: Yes! The PNG files are ready for presentations and documentation.

**Q: How do I regenerate diagrams?**  
A: Use the Docker command shown above in "Common Tasks".

**Q: What if I don't have Docker?**  
A: Install PlantUML CLI or use the online editor.

**Q: Are these diagrams up to date?**  
A: Yes, generated on April 12, 2026 from the latest design.

**Q: Can I modify the diagrams?**  
A: Yes! Edit the `.puml` files and regenerate.

**Q: What format are the source files?**  
A: PlantUML text format (`.puml`), easy to version control.

## 📞 Need Help?

1. Check [README.md](README.md) for detailed explanations
2. Review [INDEX.md](INDEX.md) for quick reference
3. Read the [Design Document](../documentation/Infraguard-design.md)
4. Visit [PlantUML Documentation](https://plantuml.com/)

## ✅ Checklist

- [ ] Viewed System Architecture diagram
- [ ] Understood component interactions
- [ ] Reviewed data flow
- [ ] Explored ML pipeline
- [ ] Checked deployment options
- [ ] Read security architecture
- [ ] Understood error handling
- [ ] Ready to dive deeper!

---

**Created**: April 12, 2026  
**Total Diagrams**: 12  
**Status**: ✅ Production Ready  
**Next Step**: Open `InfraGuard System Architecture.png` to start!
