# pydantic-ai-agentic-patterns

[PydanticAI](https://ai.pydantic.dev/) is my Python library of choice when it comes to building multi-agent applications.

It provides a simple, flexible and intuitive way to define and compose AI agents.

This repo shows various examples of multi-agent patterns implemented using PydanticAI.

## Getting Started

```bash
make install
```

This uses `uv` to install the dependencies.

Once installed you can run the examples.

> While these example uses [Groq](https://groq.com/) use can swap to use any [models](https://ai.pydantic.dev/models/) that PydanticAI supports.

### Agent Handoff

This example demonstrates how to implement a programmatic [agent handoff](./src/agent_handoff.md) pattern.

```bash
python src/agent_handoff.py
```

## License

This project is licensed under the MIT License
