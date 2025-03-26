import re
import networkx as nx

# Sample Mermaid.js input (Replace with your actual file content)
mermaid_diagram = """
graph TD
    A[Start: User Interaction] --> B[Select Command]
    B --> C[Command: monitor]
    B --> D[Command: feedback]
    B --> E[Command: Recon]
    B --> F[Other Commands]

    %% Chat Start Flow
    A --> G[on_chat_start: Initialize Chat]
    G --> G1[Display Welcome Message]
    G1 --> G2[Ask User to Select System]
    G2 -->|General_IHub| G3[Initialize SQLiteTool for General_IHub]
    G2 -->|Catalyst| G4[Initialize SQLiteTool for Catalyst]
    G3 --> G5[Query Database for Last Month's Data]
    G4 --> G5
    G5 --> G6[Display Last Month's Data]
    G6 --> G7[Ask User to Upload New Month-End Data]
    G7 -->|Uploaded| G8[Validate and Insert Data into Database]
    G8 --> G9[Run Anomaly Detection]
    G9 --> G10[Display Anomaly Detection Results]
    G10 --> G11[Ask User to Take Action on Anomalies]
    G11 -->|Proceed| G12[Handle Anomalies and Create JIRA Tickets]
    G11 -->|Cancel| G13[End Interaction]

    %% Monitor Command Flow
    C --> C1[Call jira_monitor.monitor_recent_jira_comment]
    C1 --> C2[Generate Plan of Action]
    C2 --> C3[Ask User: Execute Plan?]
    C3 -->|Yes| C4[Execute Automation Task]
    C3 -->|No| C5[Cancel Execution]

    %% Feedback Command Flow
    D --> D1[Call handle_feedback]
    D1 --> D2[Fetch Records from Database]
    D2 --> D3[Display Records to User]
    D3 --> D4[Update Database Based on Feedback]

    %% Recon Command Flow
    E --> E1[Initialize ReactAgent]
    E1 --> E2[Process Query with ReactAgent]
    E2 --> E3[Return Response to User]

    %% Other Commands Flow
    F --> F1[Process Query with ReactAgent]
    F1 --> F2[Return Response to User]

    %% Styling
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C,D,E,F,G fill:#ccf,stroke:#333,stroke-width:1px
    style G1,G2,G3,G4,G5,G6,G7,G8,G9,G10,G11,G12,G13 fill:#fff,stroke:#333,stroke-width:1px
    style C1,C2,C3,C4,C5,D1,D2,D3,D4,E1,E2,E3,F1,F2 fill:#fff,stroke:#333,stroke-width:1px
"""

# Regex to extract nodes and edges
node_pattern = re.compile(r'(\w+)\[([^\]]+)\]')  # Matches nodes like A[Start: User Interaction]
edge_pattern = re.compile(r'(\w+)\s*-->\|?([^|]*)\|?\s*(\w+)')  # Matches edges like A --> B or A -->|Label| B

# Parse nodes
nodes = {match[0]: match[1] for match in node_pattern.findall(mermaid_diagram)}

# Parse edges
edges = edge_pattern.findall(mermaid_diagram)

# Create Structurizr DSL
dsl_code = ["workspace {", "    model {"]

# Add elements
for key, value in nodes.items():
    dsl_code.append(f'        {key} = softwareSystem "{value}"')

# Add relationships
for source, label, target in edges:
    label = label.strip()  # Clean up the label
    if label:
        dsl_code.append(f'        {source} -> {target} : "{label}"')
    else:
        dsl_code.append(f'        {source} -> {target}')

dsl_code.append("    }")
dsl_code.append("}")

# Save to file
with open("output.dsl", "w") as file:
    file.write("\n".join(dsl_code))

print("✅ Structurizr DSL file (output.dsl) generated successfully!")