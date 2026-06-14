from multiprocessing import context
from urllib import response

from click import prompt
import gradio as gr
from pymongo import MongoClient
from urllib.parse import quote_plus
import certifi
from mlx_lm import load, generate
import re
import time
from dotenv import load_dotenv
import os


def strip_thinking(response: str) -> str:
    # Removes <think>...</think> including any whitespace/newline variants
    response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
    return response.strip()

qwen_start = time.time()
print("Loading Qwen...")
model, tokenizer = load("mlx-community/Qwen3-8B-4bit")
print(f"Model ready! ({time.time() - qwen_start:.2f}s)")
#measuring time
# ── MongoDB setup ──────────────────────────────────────────────────────────────
load_dotenv()

username = os.getenv("MONGO_USER")
password = quote_plus(os.getenv("MONGO_PASSWORD"))

uri = f"mongodb+srv://{username}:{password}@firstcluster.wvt5kz6.mongodb.net/?appName=FirstCluster"

client = MongoClient(
    uri,
    tlsCAFile=certifi.where()
)

print(client.admin.command("ping"))

db = client["shreyash_ai"]
documents_collection = db["documents"]# ── Cache context at startup, not on every call ────────────────────────────────
print("Fetching documents from MongoDB...")
_cached_context = None

def get_context():
    global _cached_context
    if _cached_context is None:
        context = ""
        for doc in documents_collection.find():
            context += f"\n\nDocument: {doc['title']}\n"
            context += doc["content"][:2000]#  Limit to first 2000 characters
        _cached_context = context[:8000]
    return _cached_context

# Pre-warm the cache immediately
mongo_start = time.time()
get_context()
print(f"Context cached! ({time.time() - mongo_start:.2f}s)")

# ── Inference ──────────────────────────────────────────────────────────────────
def answer_question(question):
    request_start = time.time()
    step = time.time()
    context = get_context()
    print(f"Context retrieval: {time.time()-step:.2f}s")
    print(f"Context length: {len(context)} chars")
    messages = [
        {
            "role": "system",
            "content": (
                f"Use the following documents as reference when answering.\n"
                f"{context}\n"
                f"Limit responses to 50 words. Do not include reasoning or thinking."
            ),
        },
        {"role": "user", "content": question},
    ]

    prompt = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=False  # stops the model generating <think> at all
    )
    print(f"Prompt build: {time.time()-step:.2f}s")
    token_start = time.time()
    tokens = tokenizer.encode(prompt)
    print(f"Prompt tokens: {len(tokens)}")
    print(f"Tokenization: {time.time()-token_start:.2f}s")

    generation_start = time.time()
    response = generate(
    model,
    tokenizer,
    prompt=prompt,
    max_tokens=150,
    verbose=False
    )
    print(f"Generation: {time.time()-generation_start:.2f}s")
    response = strip_thinking(response)  # ← replaces your old if/split block
    print(f"TOTAL REQUEST: {time.time()-request_start:.2f}s")
    return response


# ── UI ─────────────────────────────────────────────────────────────────────────
demo = gr.Interface(
    fn=answer_question,
    inputs=gr.Textbox(label="Your Question"),
    outputs=gr.Textbox(label="Answer"),
    title="ShreyCreys Assistant",
)
demo.launch()