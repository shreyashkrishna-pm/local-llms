HI!
This is usage of Local AI assistant powered by 

- Qwen 3 - LLM
- MongoDB Atlas - Database
- Python - document retrieval for resume, cover letter, and knowledge management workflows


1. Documents are processed through DB_MongoDB.py:
   - Read PDF files from the documents/ folder
   - Extract text using PyPDF
   - Store content in MongoDB

2. App.py serves as the execution layer:
   - Accept user questions
   - Retrieve relevant document context
   - Construct prompts for Qwen
   - Generate responses locally
   - Return concise answers through the UI

Latency Measures

- Qwen Model Load	~2.8s
- MongoDB Context Fetch	~0.8s
- Total Application Startup	~3.6s
- Context Retrieval	<0.01s
- Prompt Construction	~0.02s
- Tokenization	<0.01s
- Response Generation	~7.3s
- End-to-End Response Time	~7.5s

Thank you for checking out this project. I hope it helps you explore, build, and experiment with local LLMs, Retrieval-Augmented Generation (RAG), and personal AI assistants on Apple Silicon Macs.
Note: The current implementation is designed and tested for Apple Silicon devices (M1/M2/M3/M4) using MLX.
