# Diagram sources

This project intentionally uses several diagram formats instead of Mermaid:

- `architecture.dot`: Graphviz system architecture
- `oauth-sequence.puml`: PlantUML OAuth sequence
- `queue-state.dot`: Graphviz state machine
- README ASCII flow: plain-text operational diagram

Rendered SVG files are committed so diagrams display directly on GitHub without
requiring a browser plugin.

To regenerate with local tools:

```powershell
dot -Tsvg architecture.dot -o architecture.svg
dot -Tsvg queue-state.dot -o queue-state.svg
java -jar plantuml.jar -tsvg oauth-sequence.puml
```
