import asyncio
from database import search_knowledge_base, init_pool, close_pool
from calculator import calculate_system

async def test_all():
    print("🚀 Starting Verification...")
    await init_pool()

    # 1. TEST RAG
    print("\n--- Testing RAG Retrieval ---")
    query = "grid schedule"
    print(f"Query: '{query}'")
    context = await search_knowledge_base(query)
    print(f"Result:\n{context}")
    
    if "Yangon" in context:
        print("✅ RAG Test PASSED")
    else:
        print("❌ RAG Test FAILED")

    # 2. TEST CALCULATOR
    print("\n--- Testing Calculator ---")
    # 2000W for 4 hours = 8kWh -> Should hit Tier C or D
    res = await calculate_system(2000, 4, "home")
    print(f"Result: {res.get('tier_name')} | {res.get('specs')}")
    
    if res.get('strategy') == 'HOME_INSTALL':
         print("✅ Calculator Test PASSED")
    else:
         print("❌ Calculator Test FAILED")

    await close_pool()

if __name__ == "__main__":
    asyncio.run(test_all())
