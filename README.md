# ResumeOptimizer
flowchart TD
    A[📥 entrypoint.py<br>Load Resume + JD] --> B[🧠 parsing_module.py<br>Split into Sections]
    B --> C[📄 experience_splitter.py<br>Chunk Work History into Jobs]
    A --> D[🧾 keyword_matcher.py<br>Extract Raw + GPT-filtered Keywords]
    D --> E[🧮 keyword_classifier.py<br>(Optional) Label Keyword Types]
    E --> F[🧠 keyword_scorer.py<br>Score Keywords (ATS Style)]
    C --> G[✍️ llm_enhancer.py<br>Enhance Resume with GPT]
    G --> H[🧠 workflow.py<br>Execute all above steps in order and Run Entire Pipeline]
    H --> I[🧠 keyword_scorer.py<br>Check improved keyword match (Re-score)]
    I --> J[🧠 entrypoint.py<br>Display updated resume, match score
