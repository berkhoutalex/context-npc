import os
from dotenv import load_dotenv
from src.context_npc import NPCGenerator

if __name__ == "__main__":
    load_dotenv()
    gen = NPCGenerator(campaign_id = os.getenv("CAMPAIGN_ID"))
    context = gen._location_context("Cool City")
    npc1 = gen.gen_character(context)
    print(npc1)
    npc2 = gen.gen_character(context, 1)
    print(npc2)
    npc3 = gen.gen_character(context, 10)
    print(npc3)