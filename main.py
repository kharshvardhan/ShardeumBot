import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import discord
import os
from keep_alive import keep_alive


## Preparing for dynamic question from google sheets
faq_data = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vQYeuQsSGW3HW0pYIr2lkp2i01fL4mR0tvqT8mUt062B7UxXuuaAr6oBgbfrcZ0bsFyOTIiBVQxu9Me/pub?gid=0&single=true&output=csv")
command_list_auto_generated = []
id_answer_doc_list = {}
question_answer_doc_list = {}
search_doc_list = []
for row in faq_data.to_dict("records"):
  command_list_auto_generated += ["** !{id}** - {question}".format(id=row['id'], question=row['question'])]
  id_answer_doc_list[str(row['id'])] = row
  question_answer_doc_list[row['question'].lower()] = row
  search_doc_list += [[row['id'], row['question'].lower(), row['question']]]

## Preparing for admin commands
statement_hello_command = """
How may I help you?  

Type **!commands** to see what all can I do.

Can't find a question **!<word>** to search for it.

Click to join:  
  - Shardeum server [👉link](https://discord.gg/RsyGB8xKU7)  
  - Shardeum Times server [👉link](https://discord.gg/HDWZ2vAAez)  
"""
list_of_admin_commands = {'commands': {'answer':"""Write the **!QuestionNumber** to get the answer. \n
Can't find a question **!<word>** to search for it.\n\n
Here are some frequently asked questions:
{}
 """.format("\n\n".join(command_list_auto_generated))},
                          'hello':{'answer':statement_hello_command},
                          'hi':{'answer':statement_hello_command},
                          'hey':{'answer':statement_hello_command}}

## Preparing for search feature
vectorizer = TfidfVectorizer()

threshold = 0.4

def search_question_based_on_entry(message_string):
  df = pd.DataFrame(columns=["ID","DESCRIPTION","Question"], data=np.matrix(search_doc_list))
  corpus = list(df["DESCRIPTION"].values)
  element_comparor_id = len(corpus)
  corpus += [message_string]
  X = vectorizer.fit_transform(corpus)
  potential_match_list = []

  for x in range(0,X.shape[0]-1):
    sentence_similarity = cosine_similarity(X[x],X[element_comparor_id])
    # print(sentence_similarity, df["Question"][x])
    if (sentence_similarity>threshold):
      potential_match_list += [{'id':df["ID"][x], 'question':df["Question"][x]}]
  
  return potential_match_list

## Creating the function to be used to analyze incoming commands and creation directional flow
def message_processor(message_content):
  if message_content in list(list_of_admin_commands.keys()):
    question_found = list_of_admin_commands[message_content]
    return {'body':'{}'.format(question_found['answer']),
           'title':message_content}

  if message_content in list(id_answer_doc_list.keys()):
    question_found = id_answer_doc_list[message_content]
    return {'body':'{}'.format(question_found['answer']),
            'title':question_found['question']}

  if message_content in list(question_answer_doc_list.keys()):
    question_found = question_answer_doc_list[message_content]
    return  {'body':'{}'.format(question_found['answer']),
            'title':question_found['question']}

  search_for_question = search_question_based_on_entry(message_content)
  search_options = []
  if len(search_for_question) > 0:
    for x in search_for_question:
      search_options += ["** !{}** - {}".format(x['id'], x['question'])]
    return {'body':'Did you mean: \n\n{}'.format("\n\n".join(search_options)),
           'title':'Search results for "{}"'.format(message_content)}
  else:
    found_match_string = [x for x in list(question_answer_doc_list.keys()) if message_content.lower() in x.lower()]
    if len(found_match_string) > 0:
      for k, v in question_answer_doc_list.items():
        if k in found_match_string:
          search_options += ["** !{}** - {}".format(v['id'], v['question'])]

      if len(search_options) > 0:
        return {'body':'Did you mean:\n\n{}'.format("\n\n ".join(search_options)),
                'title':'Search results for "{}"'.format(message_content)}
      else:
        return None

  return None

## Function to format the message before sending the message
def format_embed(ctx, title=embed_title, url=embed_url, description=embed_description):
  embed = discord.Embed(title=title, url=url, description=description)
  embed.set_author(name=ctx.author.display_name,  icon_url=ctx.author.avatar_url)
  embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/1503300887900753927/CcKkS39__400x400.jpg")
  # embed.set_footer(text="Can't find a question **!<word>** to search for it.")
  return embed

## Initiating discord service
client = discord.Client()

embed = discord.Embed()
embed_color = "0xFF5733"
embed_title = "Hi!"
embed_url = "https://discord.gg/HDWZ2vAAez"
embed_description = statement_hello_command

@client.event
async def on_ready():
  print('We have logged in as {0.user} '.format(client))
  
@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content == ("!reset"):
    faq_data = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vQYeuQsSGW3HW0pYIr2lkp2i01fL4mR0tvqT8mUt062B7UxXuuaAr6oBgbfrcZ0bsFyOTIiBVQxu9Me/pub?gid=0&single=true&output=csv")
    command_list_auto_generated = []
    id_answer_doc_list = {}
    question_answer_doc_list = {}
    search_doc_list = []
    for row in faq_data.to_dict("records"):
      command_list_auto_generated += ["!{id} !{question}".format(id=row['id'], question=row['question'])]
      id_answer_doc_list[str(row['id'])] = row
      question_answer_doc_list[row['question'].lower()] = row
      search_doc_list += [[row['id'], row['question'].lower(), row['question']]]
    
    list_of_admin_commands = {'commands': {'answer':"""Write the **!QuestionNumber** to get the answer. \n
Can't find a question **!<word>** to search for it.\n\n
Here are some frequently asked questions:
{}
 """.format("\n".join(command_list_auto_generated))},
                              'hello':{'answer':statement_hello_command},
                              'hi':{'answer':statement_hello_command},
                              'hey':{'answer':statement_hello_command}}

  if message.content.startswith("!"):
    
    message_content = message.content[1:].lower()
    analyzing_message = message_processor(message_content)
    if analyzing_message is None:
      await message.channel.send( embed=format_embed(message) )
    else:
      await message.channel.send( embed=format_embed(message, title=analyzing_message['title'], description=analyzing_message['body']) )

keep_alive()  
client.run(os.getenv('TOKEN'))
