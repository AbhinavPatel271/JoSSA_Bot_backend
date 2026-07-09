<h1>Josh AI — JoSAA Counselling Chatbot</h1>

<p>A public-facing agentic chatbot helping students navigate JoSAA college allotment with personalized college and branch recommendations.</p>

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB"/>
  <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=flat&logo=mongodb&logoColor=white"/>
  <img src="https://img.shields.io/badge/Vercel-000000?style=flat&logo=vercel&logoColor=white"/>
  <img src="https://img.shields.io/badge/Render-46E3B7?style=flat&logo=render&logoColor=white"/>
</p>

<hr/>

<h2>🚀 Features</h2>

<ul>
  <li><b>Personalized Recommendations</b> — Students enter their rank and preferences to receive tailored college and branch suggestions.</li>
  <li><b>Agentic Query Engine</b> — LLM-driven tool calling orchestrating document QA, placement queries, rank recommendations, college comparisons, and web search.</li>
  <li><b>OR-CR Data Integration</b> — Official Opening and Closing Rank data imported into MongoDB for dynamic, real-time rank-based querying.</li>
  <li><b>RAG Pipeline</b> — FAISS-powered vector search with Groq-powered LLM inference for fast, low-latency responses.</li>
  <li><b>Placement Insights</b> — Placement data from 40+ institutes integrated alongside official JoSAA resources for accurate, dependable responses.</li>
  <li><b>Interactive Chat</b> — Ask follow-up questions after receiving recommendations for a complete counselling experience.</li>
</ul>

<hr/>

<h2>🛠️ Tech Stack</h2>

<table>
  <thead>
    <tr>
      <th>Layer</th>
      <th>Technology</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Frontend</td><td>JavaScript, CSS, Vercel</td></tr>
    <tr><td>Backend</td><td>Python, FastAPI, Render</td></tr>
    <tr><td>LLM Inference</td><td>Groq API</td></tr>
    <tr><td>Vector Search</td><td>FAISS</td></tr>
    <tr><td>Database</td><td>MongoDB</td></tr>
  </tbody>
</table>

<hr/>

<h2>🏗️ Architecture</h2>

<pre>
User Input (Rank / Details)
        ↓
Agentic Query Engine (LLM Tool Calling)
        ↓
┌─────────────────────────────────────────┐
│  Document QA   │   Web Search           │
│  OR-CR Query   │   Placement Insights   │
│  Rank Reco     │   College Comparisons  │
└─────────────────────────────────────────┘
        ↓
RAG Pipeline (FAISS + Groq)
        ↓
Personalized Response
</pre>

<hr/>

<h2>📊 Impact</h2>

<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>Value</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Students Served</td><td>3000+ during JoSAA 2025 counselling</td></tr>
    <tr><td>Institutes Covered</td><td>40+ with integrated placement data</td></tr>
  </tbody>
</table>

<hr/>

<h2>🙏 Acknowledgements</h2>

<ul>
  <li>Official JoSAA datasets for OR-CR data.</li>
  <li><a href="https://groq.com">Groq</a> for low-latency LLM inference.</li>
  <li><a href="https://github.com/facebookresearch/faiss">FAISS</a> by Meta AI for vector search.</li>
</ul>
