import os
from openai import OpenAI
import requests
import re

class ArticleType:
  LOCATIONS = "locations"
  FAMILIES = "families"
  CHARACTERS = "characters"
  ORGANISATIONS = "organizations"
  ITEMS = "items"
  NOTES = "notes"
  CALENDARS = "calendars"
  RACES = "races"
  QUESTS = "quests"
    

class NPCGenerator:
  root_url = "https://api.kanka.io/1.0/campaigns/"
  
  model = "gpt-3.5-turbo" 
  
  instructions = [
    { "role": "system"
    , "content": "You are used to generate new NPCS for a campaign given context from a user, which can be a location, family, character, organization, item."
    },
    { "role": "system"
    , "content": "Return the response as a json with the fields name, entry (an html description of the characters history and including a section on goals, fears and bonds), title, age, sex and location"
    },
    {
      "role": "system",
      "content": "The relatedness parameter is an integer from 1 to 10, where 1 is the least related and 10 is the most related. It is used to determine how closely the generated NPC should be related to the context given by the user."
    }
  ]
  
  
  
  def __init__(self, campaign_id: str):
    self.campaign_id = campaign_id
    
    self.headers = {
      "Authorization": "Bearer " + os.getenv("KANKA_API"),
    }
    
    self.client = OpenAI(
      api_key = os.getenv("OPENAI_API_KEY")
    )
    
    
  def gen_character(self, content, relatedness: int = 5):
    context = [ 
        { "role": "user", "content": "Relatedness: " + str(relatedness)},
        { "role": "user", "content": content }
      ]
    response = self.client.chat.completions.create(
        model=self.model,
        messages=self.instructions + context,
        temperature=0
    )
    response_message = response.choices[0].message.content
    return response_message
  
  def _location_context(self, location_name: str):
    url = self.root_url + self.campaign_id + "/locations?name=" + location_name
    response = requests.get(url, headers=self.headers)
    location_contents = response.json()
    stripped_html = re.sub('<[^<]+?>', '', location_contents["data"][0]["entry_parsed"])
    return stripped_html