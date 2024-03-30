from dataclasses import dataclass
import json
import os
import random
from typing import Optional
from openai import OpenAI
import requests
import re

@dataclass
class ApiInfo:
  count: int
  pages: int
  next: Optional[str]
  previous: Optional[str]

@dataclass
class ArticleType:
  LOCATIONS = "locations"
  FAMILIES = "families"
  CHARACTERS = "characters"
  ORGANISATIONS = "organisations"
  ITEMS = "items"
  NOTES = "notes"
  CALENDARS = "calendars"
  RACES = "races"
  QUESTS = "quests"
  
  
class Character:


  def __init__(self, name, entry,age, sex, appearance, personality):
    self.name = name
    self.entry = entry
    self.age = age
    self.sex = sex 
    self.appearance = appearance
    self.personality = personality
    
  def __str__(self):
    return f"{self.name} : {self.entry}"
  
  def submit(self, campaign_id: str):
    url = "https://api.kanka.io/1.0/campaigns/" + campaign_id + "/characters"
    data = {
      "name": self.name,
      "entry": self.entry,
      "age": self.age,
      "sex": self.sex,
      "appearance_name": ["Appearance"],
      "appearance_entry": [self.appearance],
      "personality_name": ["Personality"],
      "personality_entry": [self.personality]
    }
    
    headers = {
      "Authorization": "Bearer " + os.getenv("KANKA_API"),
    }
    
    response = requests.post(url, headers=headers, json=data)
      
    

class NPCGenerator:
  root_url = "https://api.kanka.io/1.0/campaigns/"
  
  model = "gpt-3.5-turbo" 
  
  instructions = [
    { "role": "system"
    , "content": "You are used to generate new NPCS for a campaign given context from a user, which can be a location, family, character, organization, item."
    },
    { "role": "system"
    , "content": "Return the response as a json with the fields name, entry (an html description of the characters history and including a section on goals, fears and bonds), age, sex"
    },
    { "role": "system"
    , "content": "Additionally provide in the json an appearance field which is a description of the characters physical appearance and a personality field which is a description of the characters personality."
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
    
    
  def gen_character(self, content):
    context = [ 
        { "role": "user", "content": content }
      ]
    response = self.client.chat.completions.create(
        model=self.model,
        messages=self.instructions + context,
        temperature=0
    )
    response_message = json.loads(response.choices[0].message.content)
    return Character(
      name = response_message["name"],
      entry = response_message["entry"],
      age = response_message["age"],
      sex = response_message["sex"],
      personality= response_message["personality"],
      appearance = response_message["appearance"]
    )
  
  def _generic_context(self, context_type: str, name: str):
    url = self.root_url + self.campaign_id + "/" + context_type + "?name=" + name
    response = requests.get(url, headers=self.headers)
    contents = response.json()
    stripped_html = re.sub('<[^<]+?>', '', contents["data"][0]["entry_parsed"])
    return stripped_html
  
  
  def _get_article_page(self, url):
    response = requests.get(url, headers=self.headers)
    contents = response.json()
    info = ApiInfo(
      count = contents["meta"]["total"],
      pages = contents["meta"]["last_page"],
      next = contents["links"]["next"],
      previous = contents["links"]["prev"])
    return contents["data"], info
  
  def _get_article_list(self, context_type: str):
    print(context_type)
    initial_url = self.root_url + self.campaign_id + "/" + context_type
    data, info = self._get_article_page(initial_url)
    while info.next:
      next_data, info = self._get_article_page(info.next)
      data += next_data
    return data
  
  def _random_context(self):
    article_types =  \
        [ ArticleType.LOCATIONS
        # , ArticleType.FAMILIES
        , ArticleType.CHARACTERS
        , ArticleType.ORGANISATIONS
        # , ArticleType.ITEMS
        , ArticleType.NOTES
        # , ArticleType.CALENDARS
        , ArticleType.RACES
        # , ArticleType.QUESTS
        ]
    context_type = random.choice(article_types)
    response = self._get_article_list(context_type)
    random_article = random.choice(list(filter(lambda r: r["entry_parsed"] is not None, response)))
    stripped_html = re.sub('<[^<]+?>', '', random_article["entry_parsed"])
    return stripped_html