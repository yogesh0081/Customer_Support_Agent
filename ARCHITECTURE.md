# Architecture — ShopEasy Customer Support Agent

## System Flow
```
User → Input Guardrail → Sentiment Guardrail → Behavioral Guardrail
     → Planner Agent → Executor Agent → Critic Agent
     → Output Guardrail → Final Response
```

## Component Details

| Component | File | Responsibility |
|---|---|---|
| Orchestrator | src/agent.py | Runs full pipeline |
| Planner | src/multi_agent.py | Decides tool and goal |
| Executor | src/multi_agent.py | Runs tool, generates response |
| Critic | src/multi_agent.py | Reviews quality (1-10) |
| Guardrails | src/guardrails.py | 4 guardrail layers |
| Tools | src/tools.py | FAQ, order, escalation |
| Memory | src/memory.py | Persistent user data |
| Logger | src/logger.py | Session logging |
| UI | app.py | Streamlit chat interface |

## Guardrail Decision Tree
```
Input received
    ├── Empty? → Pass through
    ├── Prompt injection keywords? → BLOCK
    ├── Harmful/off-topic keywords? → BLOCK
    ├── Angry sentiment? → ESCALATE
    ├── Off-domain topic? → BLOCK
    └── Pass to multi-agent pipeline
            └── Output generated
                    ├── Hallucination patterns? → REPLACE
                    ├── Unsafe content? → REPLACE
                    └── Return safe response
```

## Data Flow
```
user_memory.json ←→ memory.py ←→ agent.py
faq.json         ←→ tools.py  ←→ multi_agent.py
logs/            ←→ logger.py ←→ agent.py
.env             ←→ config.py ←→ all modules
```