import os
from dotenv import load_dotenv
from src.context_npc import NPCGenerator, ArticleType

if __name__ == "__main__":
    load_dotenv()
    gen = NPCGenerator(campaign_id = os.getenv("CAMPAIGN_ID"))
    context = gen._random_context()
    npc1 = gen.gen_character(context)
    print(npc1)
    npc1.submit(gen.campaign_id)