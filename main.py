from crewai import LLM
import os  
import json  
from datetime import datetime  
from transformers import pipeline  
import yfinance as yf  
import time  
import random  

# --- CONFIGURATION ---
loki_brain = LLM(model="ollama/phi3", base_url="http://localhost:11434")


# --- MEMORY SYSTEM ---  
def load_memory():  
    try:  
        with open("memory.json", "r") as f:  
            return json.load(f)  
    except:  
        return {
            "successes": [], 
            "failures": [], 
            "rewires": 0, 
            "last_prompts": {
                "content": "Write a blog post about AI tools for passive income", 
                "affiliate": "Create optimized affiliate links for AI courses"
            }
        }  

def save_memory(data):  
    with open("memory.json", "w") as f:  
        json.dump(data, f, indent=4)  

def rewire_prompts(memory):  
    if len(memory["failures"]) > 3 and memory["rewires"] < 5:  
        memory["last_prompts"]["content"] += " with SEO keywords like 'AI passive income 2026'."  
        memory["last_prompts"]["affiliate"] += " including high-converting calls-to-action."  
        memory["rewires"] += 1  
        print(f"🛠️ Rewired prompts: {memory['last_prompts']}")  
    return memory  

# --- TOOLS ---  
def analyze_market(symbol, is_crypto=False):  
    try:  
        ticker = yf.Ticker(f"{symbol}-USD" if is_crypto else symbol)  
        info = ticker.info  
        price = info.get('currentPrice', 'N/A')  
        change = info.get('regularMarketChangePercent', 0)  
        sentiment = "Bullish" if change > 0 else "Bearish" if change < 0 else "Neutral"  
        return f"{symbol}: Price ${price}, Change {change:.2f}%. Sentiment: {sentiment}"  
    except Exception as e:  
        return f"Analysis failed: {str(e)}"  

# --- AGENTS ---  
class AI_Agent:  
    def __init__(self, name, role, model):  
        self.name = name  
        self.role = role  
        self.model = model  

    def execute(self, input_data):  
        if callable(self.model):  
            return self.model(input_data)  
        else:  
            return self.model(input_data, do_sample=True, num_return_sequences=1)[0]['generated_text']  

Content_Creator = AI_Agent("WriterBot", "Content Generator", GENERATOR)  
Market_Analyzer = AI_Agent("MarketBot", "Market Analyst", analyze_market)  
Affiliate_Optimizer = AI_Agent("LinkBot", "Affiliate Optimizer", GENERATOR)  
Summarizer = AI_Agent("SummaryBot", "Summarizer", SUMMARIZER)  

# --- FLYWHEEL LOOP ---  
def flywheel_cycle():  
    memory = load_memory()  
    memory = rewire_prompts(memory)  
    print(f"\n🧠 Status: {len(memory['successes'])} successes, {len(memory['failures'])} failures")  

    content_prompt = memory["last_prompts"]["content"]  
    content = Content_Creator.execute(content_prompt)  
    
    stock_analysis = Market_Analyzer.execute("AAPL")  
    crypto_analysis = Market_Analyzer.execute("BTC", is_crypto=True)  
    market_insights = f"Stock: {stock_analysis}\nCrypto: {crypto_analysis}"  

    affiliate_prompt = memory["last_prompts"]["affiliate"] + f" based on: {market_insights[:100]}"  
    affiliate_links = Affiliate_Optimizer.execute(affiliate_prompt)  

    full_output = f"Content: {content[:300]}\nInsights: {market_insights}\nLinks: {affiliate_links[:300]}"  
    summary = Summarizer.execute(full_output)  

    if random.random() < 0.2:  
        memory['failures'].append({"time": str(datetime.now()), "task": "Simulated failure"})  
    else:  
        memory['successes'].append({"time": str(datetime.now()), "task": "Cycle completed"})  
    save_memory(memory)  

if __name__ == "__main__":  
    print("🚀 Autonomous-L.O.K.I. System Active")  
    while True:  
        try:  
            flywheel_cycle()  
            print("\n✅ Cycle completed. Sleeping for 1 hour...")  
            time.sleep(3600)  
        except Exception as e:  
            print(f"\n⚠️ Error: {str(e)}")  
            time.sleep(60)

