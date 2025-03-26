workspace {
    model {
        A = softwareSystem "Start: User Interaction"
        B = softwareSystem "Select Command"
        C = softwareSystem "Command: monitor"
        D = softwareSystem "Command: feedback"
        E = softwareSystem "Command: Recon"
        F = softwareSystem "Other Commands"
        G = softwareSystem "on_chat_start: Initialize Chat"
        G1 = softwareSystem "Display Welcome Message"
        G2 = softwareSystem "Ask User to Select System"
        G3 = softwareSystem "Initialize SQLiteTool for General_IHub"
        G4 = softwareSystem "Initialize SQLiteTool for Catalyst"
        G5 = softwareSystem "Query Database for Last Month's Data"
        G6 = softwareSystem "Display Last Month's Data"
        G7 = softwareSystem "Ask User to Upload New Month-End Data"
        G8 = softwareSystem "Validate and Insert Data into Database"
        G9 = softwareSystem "Run Anomaly Detection"
        G10 = softwareSystem "Display Anomaly Detection Results"
        G11 = softwareSystem "Ask User to Take Action on Anomalies"
        G12 = softwareSystem "Handle Anomalies and Create JIRA Tickets"
        G13 = softwareSystem "End Interaction"
        C1 = softwareSystem "Call jira_monitor.monitor_recent_jira_comment"
        C2 = softwareSystem "Generate Plan of Action"
        C3 = softwareSystem "Ask User: Execute Plan?"
        C4 = softwareSystem "Execute Automation Task"
        C5 = softwareSystem "Cancel Execution"
        D1 = softwareSystem "Call handle_feedback"
        D2 = softwareSystem "Fetch Records from Database"
        D3 = softwareSystem "Display Records to User"
        D4 = softwareSystem "Update Database Based on Feedback"
        E1 = softwareSystem "Initialize ReactAgent"
        E2 = softwareSystem "Process Query with ReactAgent"
        E3 = softwareSystem "Return Response to User"
        F1 = softwareSystem "Process Query with ReactAgent"
        F2 = softwareSystem "Return Response to User"
        B -> General_IHub : "C[Command: monitor]
    B --> D[Command: feedback]
    B --> E[Command: Recon]
    B --> F[Other Commands]

    %% Chat Start Flow
    A --> G[on_chat_start: Initialize Chat]
    G --> G1[Display Welcome Message]
    G1 --> G2[Ask User to Select System]
    G2 -->"
        G2 -> G4 : "Catalyst"
        G3 -> Uploaded : "G5[Query Database for Last Month's Data]
    G4 --> G5
    G5 --> G6[Display Last Month's Data]
    G6 --> G7[Ask User to Upload New Month-End Data]
    G7 -->"
        G8 -> Proceed : "G9[Run Anomaly Detection]
    G9 --> G10[Display Anomaly Detection Results]
    G10 --> G11[Ask User to Take Action on Anomalies]
    G11 -->"
        G11 -> G13 : "Cancel"
        C -> Yes : "C1[Call jira_monitor.monitor_recent_jira_comment]
    C1 --> C2[Generate Plan of Action]
    C2 --> C3[Ask User: Execute Plan?]
    C3 -->"
        C3 -> C5 : "No"
        D -> x : "D1[Call handle_feedback]
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
    style C1,C2,C3,C4,C5,D1,D2,D3,D4,E1,E2,E3,F1,F2 fill:#fff,stroke:#333,stroke-width:1p"
    }
}