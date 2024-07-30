""" Aim: Cross Domain Recommendation System using LLMs (Open AI) App

Author : Yesh - Neo Corp
"""

import requests
import json

import chromadb
from chromadb import Settings

## Calling to OpenAI
from openai import OpenAI

# api keys
openai_api_key = "sk-proj-lx3gJyUf4CBET9kL6CyIT3BlbkFJtgKPJfzidV0Kzn66y8PV"

verbose = "True"

## TODO : Check whether the vector db present or not
## 

if verbose:
    print("Info: Initiating vector db!")

client = chromadb.PersistentClient(path="vectordb1",settings=Settings(allow_reset=True))
# loading the collection
collection = client.get_collection(name="RecSysCollection")

if verbose:
    print("Info: Vector db initiating and collection fetched successfuly!")

def getNearProduct( domain, product, n_results=2):
    # takes domain, product, number of results to show
    # returns nearest products in that domain
    global collection

    results = collection.query(
        query_texts = [product],
        n_results = n_results,
        where = {"domain": domain},
        include = [ "metadatas", "documents"]
    )
    out = {}
    keys = [ 'ids' , 'metadatas' , 'documents']
    for key in keys:
        out[key] = results[key]
    return out

## Twitter :: Start
bearer_token = "AAAAAAAAAAAAAAAAAAAAAIbMtwEAAAAAqw5oqOo3o07SCqa1VZPPkEH5jf8%3D0OYxcrWdjl6KlCB9bNstF5j2Au3U4LWx85lbG83wRF3vn9rOdc"

def create_url(username):
    # Specify the usernames that you want to lookup below
    # You can enter up to 100 comma-separated values.
    usernames = "usernames={}".format(username)
    user_fields = "user.fields=description,created_at"
    # User fields are adjustable, options include:
    # created_at, description, entities, id, location, name,
    # pinned_tweet_id, profile_image_url, protected,
    # public_metrics, url, username, verified, and withheld
    url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, user_fields)
    return url


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth,)
    # print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def getUserId(username):
    url = create_url(username)
    json_response = connect_to_endpoint(url)
    # print(json.dumps(json_response, indent=4, sort_keys=True))
    return json_response['data'][0]['id']

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
# bearer_token = os.environ.get("BEARER_TOKEN")


def create_url_tweets(userid):
    # Replace with user ID below
    # user_id = 721835017169739776
    return "https://api.twitter.com/2/users/{}/tweets".format(userid)


def get_params_tweets():
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    return {"tweet.fields": "created_at,attachments,context_annotations"}


def connect_to_endpoint_tweets(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    # print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def getTweets(userid):
    url = create_url_tweets(userid)
    params = get_params_tweets()
    json_response = connect_to_endpoint_tweets(url, params)
    # print(json.dumps(json_response, indent=4, sort_keys=True))
    # TODO : filter required fields
    return json_response['data']

def getPersonality(username):
    
    userid = getUserId(username)
    tweets = getTweets(userid)

    instruct = """You are an expert in creating personality based on few inputs about the user. You were given twitter posts. \
            Analyze each and every twitter post and create a lenghty personality about the user. Give me information about his likes, \
            dislikes, domain he is intrested in etc
            """
    twitter_post_texts = "\n".join([t['text'] for t in tweets])

    prompt = f"""You are expert in creating personality of user based on twitter posts. You were given twiiter posts of the user\
            Analyze them carefully and create a lenghty descriptive personality of the user. 
            
            Here are the twitter posts:
            {twitter_post_texts}
            
            Here is the personality: 
            """
    personality = callOpenAI(prompt,instruct)
    return personality
    

## Twitter ::> End


client = OpenAI(api_key=openai_api_key)

# calling open ai
def callOpenAI(prompt,instruct):
    completion = client.chat.completions.create(
        model="gpt-4-turbo",
      messages=[
        {"role": "system", "content":instruct},
        {"role": "user", "content": prompt}
      ]
    )
    return completion.choices[0].message.content

# TODO: not used remove.
def getRecommendHelper(selection,personality):

    recommendation_object = {}
    for domain,products in selection.items():
        ## for each product get nearest top 2 products
        for product in products:
            near_products = getNearProduct(domain,product,n_results=5)
            near_products_formatted = []
            for meta, doc in zip(near_products['metadatas'][0],near_products['documents'][0]):
                obj = {
                    "product":doc
                }
                if 'image_url' in meta:
                    obj["image_url"] = meta["image_url"]
                else:
                    obj["image_url"]=""
                    
                near_products_formatted.append(obj)
        recommendation_object[domain] = near_products_formatted[1:]

    recommend = {}

    for domain, products in recommendation_object.items():
        selection_texts = "\n".join(selection[domain])
        choices = ""

        for p in products:
            choice = "Product: {} \n Image link: {} \n\n".format(p['product'], p['image_url'])
            choices+= choice

        template_4 = f"""Task: Generate a product recommendation based on the user purchases and his personlity.
            Role: You are an expert in recommending products to user based on his preferences,selection and past purchases.\
            Additionaly you were given his personality generated from his twiiter posts. You were given few choices which are similar \
            products to the user already purchased. You need to select the best product among the choices. 

            Input Data: 
                1. User purchased products:
                    {selection_texts}

                2. User personality:
                    {personality}
                    
            Desired Output: Recommend the best product among the below choices.  
            Here the choices analyze them carefully and select best one user might purchase next.
                Choices:
                {choices}

            Recommendation Logic:
            To generate a relevant product recommendation for the given user, follow these steps:
                Personality: Analyze user personality and understand his likes and dislikes.
                
                Previous purchases: Determine the taste and user preferrences.

                Match Choices: Compare the user's preferences with the provided choices.

                Recommend Product: Select the best product from the choices that best aligns with the user preferences. 
            Note: Just give me the recommended product and reasoning. 
            """
        instruct = """You are an advance recommendation system. Recommend best product among the choices."""
        domain_recommendation = callOpenAI(template_4,instruct)
        recommend[domain] = domain_recommendation

    return recommend


def getRecommendation(selection,personality): 
    ## selection => recommendation
    """
    selection = {
            "All_Beauty":[
                "Toenails Artificial Transparent Nail Tips Nail Art",
                "Howard LC0008 Leather Conditioner, 8-Ounce (4-Pack)"
            ],
            "Amazon_Fashion":[
                "Egowz High Visibility Nylon Latex Foam Coated Work Gloves",
                "YUEDGE 5 Pairs Men's Moisture Control Cushioned Dry Fit Casual Athletic Crew Socks for Men (Blue, Size 9-12)"
            ],
            "Books":[
                "modern perspective of a young black woman living in America",
                "Monstrous Stories #4: The Day the Mice Stood Still"
                
            ],
            "Cell_Phones_and_Accessories":[
                "Rikki Knight 3D Chevron Peach on White with Anchor Flip Wallet iPhoneCase",
                "iPhone 6 Plus + Case, DandyCase Perfect PATTERNNo Chip/No Peel Flexible Slim TPU Case Cover for Apple iPhone 6 Plus (5.5 Screen) [Vintage Pink Rose Floral]"
            ],
            "Movies_and_TV":[
                "Ben 10: Alien Force (Classic)",
                "Ode to Joy: Beethoven's Symphony No. 9"
            ]
        }
    """

    recommendation_object = {
        "in-domain": {},
        "cross-domain": {},
        "top-5": [],
        "best": {}
    }
    if verbose:
        print("Info: Initiating getRecommendation Function!")
        
    if verbose:
        print("Info: Getting top near products for all domains!")
    ## In-domain recommendations
    ## keys to add ::> top_products, top_5, best_recommendation 
    ## Get near products :: Done !
    for domain, products in selection.items():
        ## for each product get nearest top 2 products
        near_products_formatted = []
        for product in products:
            near_products = getNearProduct(domain, product, n_results=5)    
            for meta, doc in zip(near_products['metadatas'][0],near_products['documents'][0]):
                obj = {
                    "product":doc
                }
                if 'image_url' in meta:
                    obj["image_url"] = meta["image_url"]
                else:
                    obj["image_url"]=""
                near_products_formatted.append(obj)
        recommendation_object["in-domain"][domain] = { "top_products" : near_products_formatted }
    if verbose:
        print("Info: Top near products done!")

    if verbose:
        print("Info: Fetching twitter personality!")
    ## Get personality :: Done !
    username = "AmeetDeshpande_"
    personality = getPersonality(username)

    if verbose:
        print("Info: Twitter personality fetched successfully!")

    if verbose:
        print("Info: In-domain => Top 5 started")
    ## Top 5 : Done !
    domains = list(selection.keys())
    for domain in domains: 
        domain_products = recommendation_object['in-domain'][domain]['top_products']

        no_of_products = 5

        selection_texts = ""
        for p in selection[domain]:
            p_text = "product name : {} \n".format(p)
            selection_texts += p_text

        choices = ""
        for p in recommendation_object['in-domain'][domain]['top_products']:
            choice = "product name : {} \nimage link: {} \n\n".format(p['product'], p['image_url'])
            choices+= choice

        ## prompt :: in-domain top products => top 5
        template = f"""Task: Generate a product recommendation based on the user purchases and his personality.
                    Role: You are an expert in recommending products to user based on his preferences,selection and past purchases.\
                    Additionaly you were given his personality generated from his twiiter posts. You were given few choices which are similar \
                    products to the user already purchased. You need to select the best product among the choices. 
                    
                    Input Data: 
                        1. User purchased products:
                            {selection_texts}
                    
                        2. User personality:
                            {personality}
                            
                    Desired Output: Recommend the best {no_of_products} products among the below choices.  
                    Here the choices analyze them carefully and select best one user might purchase next.
                        Choices:
                        {choices}
                    
                    Recommendation Logic:
                    To generate a relevant product recommendation for the given user, follow these steps:
                        Personality: Analyze user personality and understand his likes and dislikes.
                        
                        Previous purchases: Determine the taste and user preferrences.
                    
                        Match Choices: Compare the user's preferences with the provided choices.
                    
                        Recommend Product: Select the best {no_of_products} products from the choices that best aligns with the user preferences. 
                    Note: Just give me the recommended product and reasoning in following json format. 
                    {{
                        "product 1": {{
                                "product name": "",
                                "image link": "",
                                "description": "",
                                "reason": ""
                        }},
                        "product 2": {{
                                "product name": "",
                                "image link": "",
                                "description": "",
                                "reason": ""
                        }},
                        "product 3": {{
                                "product name": "",
                                "image link": "",
                                "description": "",
                                "reason": ""
                        }},
                        "product 4": {{
                                "product name": "",
                                "image link": "",
                                "description": "",
                                "reason": ""
                        }},
                        "product 5": {{
                                "product name": "",
                                "image link": "",
                                "description": "",
                                "reason": ""
                        }}
                    }}
                """
        instruct = """You are an advance recommendation system. Recommend best five products among the choices."""
        recommendation = callOpenAI(template, instruct)
        recommendation_object['in-domain'][domain]['top_5'] = recommendation
    
    if verbose:
        print("Info: In-domain Top 5 Done! ")

    if verbose:
        print("Info: In-domain Tob Best started!")
    ## top best :: Done!
    domains = list(selection.keys())
    for domain in domains: 
        domain_products = recommendation_object['in-domain'][domain]['top_products']

        no_of_products = 1

        selection_texts = ""
        for p in selection[domain]:
            p_text = "product name : {} \n".format(p)
            selection_texts += p_text

        choices = ""
        for p in recommendation_object['in-domain'][domain]['top_products']:
            choice = "product name : {} \nimage link: {} \n\n".format(p['product'], p['image_url'])
            choices+= choice

        ## prompt :: in-domain top products => top 5
        template = f"""Task: Generate a product recommendation based on the user purchases and his personality.
                    Role: You are an expert in recommending best product to user based on his preferences,selection and past purchases.\
                    Additionaly you were given his personality generated from his twiiter posts. You were given few choices which are similar \
                    products to the user already purchased. You need to select the best product among the choices. 
                    
                    Input Data: 
                        1. User purchased products:
                            {selection_texts}
                    
                        2. User personality:
                            {personality}
                            
                    Desired Output: Recommend the best {no_of_products} product among the below choices.  
                    Here the choices analyze them carefully and select best one user might purchase next.
                        Choices:
                        {choices}
                    
                    Recommendation Logic:
                    To generate a relevant product recommendation for the given user, follow these steps:
                        Personality: Analyze user personality and understand his likes and dislikes.
                        
                        Previous purchases: Determine the taste and user preferrences.
                    
                        Match Choices: Compare the user's preferences with the provided choices.
                    
                        Recommend Product: Select the best {no_of_products} product from the choices that best aligns with the user preferences. 
                    Note: Just give me the recommended product and reasoning in following json format. 
                    {{
                        "product 1": {{
                                "product name": "",
                                "image link": "",
                                "description": "",
                                "reason": ""
                        }}
                    }}
                """
        instruct = """You are an advance recommendation system. Recommend top best product among the choices."""
        recommendation = callOpenAI(template, instruct)
        recommendation_object['in-domain'][domain]['top_best'] = recommendation
    
    if verbose:
        print("Info: In-domain Top Best Done!")
    
    if verbose:
        print("Info: Cross-domain Top 5 started!")
    ## cross domain
    #### cross domain: top products => top 5 => top best
    domains = list(selection.keys())

    for domain, products in selection.items():
        ## for each product get nearest top 2 products
        near_products_formatted = []
        non_domains = [d for d in domains if d!= domain]
        for product in products:
            for d in non_domains:
                near_products = getNearProduct(d, product, n_results=1)    
                for meta, doc in zip(near_products['metadatas'][0],near_products['documents'][0]):
                    obj = {
                        "product":doc
                    }
                    if 'image_url' in meta:
                        obj["image_url"] = meta["image_url"]
                    else:
                        obj["image_url"]=""
                    near_products_formatted.append(obj)
        recommendation_object["cross-domain"][domain] = { "top_products" : near_products_formatted }

    ## Top 5 : Done !
    for domain in domains: 
        domain_products = recommendation_object['cross-domain'][domain]['top_products']

        no_of_products = 5

        selection_texts = ""
        for p in selection[domain]:
            p_text = "product name : {} \n".format(p)
            selection_texts += p_text

        choices = ""
        for p in recommendation_object['cross-domain'][domain]['top_products']:
            choice = "product name : {} \nimage link: {} \n\n".format(p['product'], p['image_url'])
            choices+= choice

        ## prompt :: in-domain top products => top 5
        template = f"""Task: Generate a product recommendation based on the user purchases and his personality.
                    Role: You are an expert in recommending products to user based on his preferences,selection and past purchases.\
                    Additionaly you were given his personality generated from his twiiter posts. You were given few choices which are similar \
                    products to the user already purchased. You need to select the best product among the choices. 
                    
                    Input Data: 
                        1. User purchased products:
                            {selection_texts}
                    
                        2. User personality:
                            {personality}
                            
                    Desired Output: Recommend the best {no_of_products} products among the below choices.  
                    Here the choices analyze them carefully and select best one user might purchase next.
                        Choices:
                        {choices}
                    
                    Recommendation Logic:
                    To generate a relevant product recommendation for the given user, follow these steps:
                        Personality: Analyze user personality and understand his likes and dislikes.
                        
                        Previous purchases: Determine the taste and user preferrences.
                    
                        Match Choices: Compare the user's preferences with the provided choices.
                    
                        Recommend Product: Select the best {no_of_products} products from the choices that best aligns with the user preferences. 
                    Note: Just give me the recommended product and reasoning in following json format. 
                    {{
                        "product 1": {{
                                "product name": "",
                                "image link": "",
                                "description": "",
                                "reason": ""
                        }},
                        "product 2": {{
                                "product name": "",
                                "image link": "",
                                "description": "",
                                "reason": ""
                        }},
                        "product 3": {{
                                "product name": "",
                                "image link": "",
                                "description": "",
                                "reason": ""
                        }},
                        "product 4": {{
                                "product name": "",
                                "image link": "",
                                "description": "",
                                "reason": ""
                        }},
                        "product 5": {{
                                "product name": "",
                                "image link": "",
                                "description": "",
                                "reason": ""
                        }}
                    }}
                """
        instruct = """You are an advance recommendation system. Recommend best five products among the choices."""
        recommendation = callOpenAI(template, instruct)
        recommendation_object['cross-domain'][domain]['top_5'] = recommendation
    if verbose:
        print("Info: Cross-domain Top 5 Done!")

    if verbose:
        print("Info: Cross-domain Top Best Started!")
    ## top best
    #### cross domain => top best
    for domain in domains: 
        domain_products = recommendation_object['cross-domain'][domain]['top_products']

        no_of_products = 1

        selection_texts = ""
        for p in selection[domain]:
            p_text = "product name : {} \n".format(p)
            selection_texts += p_text

        choices = ""
        for p in recommendation_object['cross-domain'][domain]['top_products']:
            choice = "product name : {} \nimage link: {} \n\n".format(p['product'], p['image_url'])
            choices+= choice

        ## prompt :: in-domain top products => top 5 => top 1
        template = f"""Task: Generate a product recommendation based on the user purchases and his personality.
                    Role: You are an expert in recommending best product to user based on his preferences,selection and past purchases.\
                    Additionaly you were given his personality generated from his twiiter posts. You were given few choices which are similar \
                    products to the user already purchased. You need to select the best product among the choices. 
                    
                    Input Data: 
                        1. User purchased products:
                            {selection_texts}
                    
                        2. User personality:
                            {personality}
                            
                    Desired Output: Recommend the best {no_of_products} product among the below choices.  
                    Here the choices analyze them carefully and select best one user might purchase next.
                        Choices:
                        {choices}
                    
                    Recommendation Logic:
                    To generate a relevant product recommendation for the given user, follow these steps:
                        Personality: Analyze user personality and understand his likes and dislikes.
                        
                        Previous purchases: Determine the taste and user preferrences.
                    
                        Match Choices: Compare the user's preferences with the provided choices.
                    
                        Recommend Product: Select the best {no_of_products} product from the choices that best aligns with the user preferences. 
                    Note: Just give me the recommended product and reasoning in following json format. 
                    {{
                        "product 1": {{
                                "product name": "",
                                "image link": "",
                                "description": "",
                                "reason": ""
                        }}
                    }}
                """
        instruct = """You are an advance recommendation system. Recommend top best product among the choices."""
        recommendation = callOpenAI(template, instruct)
        recommendation_object['cross-domain'][domain]['top_best'] = recommendation
    
    if verbose:
        print("Info: Cross-domain Top best done!")

    if verbose:
        print("Info: Overall Top 5 Started!")
    ## Top best : Done !
    selection_texts = ""
    choices = ""

    for domain in domains: 
        domain_products = recommendation_object['in-domain'][domain]['top_products']

        no_of_products = 5

        for p in selection[domain]:
            p_text = "product name : {} \n".format(p)
            selection_texts += p_text

        for p in recommendation_object['in-domain'][domain]['top_products']:
            choice = "product name : {} \nimage link: {} \n\n".format(p['product'], p['image_url'])
            choices+= choice
            
    
    ## prompt :: altogether top products => top 5
    template = f"""Task: Generate a product recommendation based on the user purchases and his personality.
                Role: You are an expert in recommending products to user based on his preferences,selection and past purchases.\
                Additionaly you were given his personality generated from his twiiter posts. You were given few choices which are similar \
                products to the user already purchased. You need to select the best product among the choices. 
                
                Input Data: 
                    1. User purchased products:
                        {selection_texts}
                
                    2. User personality:
                        {personality}
                        
                Desired Output: Recommend the best {no_of_products} products among the below choices.  
                Here the choices analyze them carefully and select best one user might purchase next.
                    Choices:
                    {choices}
                
                Recommendation Logic:
                To generate a relevant product recommendation for the given user, follow these steps:
                    Personality: Analyze user personality and understand his likes and dislikes.
                    
                    Previous purchases: Determine the taste and user preferrences.
                
                    Match Choices: Compare the user's preferences with the provided choices.
                
                    Recommend Product: Select the best {no_of_products} products from the choices that best aligns with the user preferences. 
                Note: Just give me the recommended product and reasoning in following json format. 
                {{
                    "product 1": {{
                            "product name": "",
                            "image link": "",
                            "description": "",
                            "reason": ""
                    }},
                    "product 2": {{
                            "product name": "",
                            "image link": "",
                            "description": "",
                            "reason": ""
                    }},
                    "product 3": {{
                            "product name": "",
                            "image link": "",
                            "description": "",
                            "reason": ""
                    }},
                    "product 4": {{
                            "product name": "",
                            "image link": "",
                            "description": "",
                            "reason": ""
                    }},
                    "product 5": {{
                            "product name": "",
                            "image link": "",
                            "description": "",
                            "reason": ""
                    }}
                }}
            """
    instruct = """You are an advance recommendation system. Recommend five products among the choices."""
    recommendation = callOpenAI(template, instruct)
    recommendation_object['top_5'] = recommendation

    if verbose:
        print("Info: Overall Top 5 Done!")

    ## top best
    ## prompt ::  top 5 => top 1
    no_of_products = 1
    template = f"""Task: Generate a product recommendation based on the user purchases and his personality.
                Role: You are an expert in recommending best product to user based on his preferences,selection and past purchases.\
                Additionaly you were given his personality generated from his twiiter posts. You were given few choices which are similar \
                products to the user already purchased. You need to select the best product among the choices. 
                
                Input Data: 
                    1. User purchased products:
                        {selection_texts}
                
                    2. User personality:
                        {personality}
                        
                Desired Output: Recommend the best {no_of_products} product among the below choices.  
                Here the choices analyze them carefully and select best one user might purchase next.
                    Choices:
                    {choices}
                
                Recommendation Logic:
                To generate a relevant product recommendation for the given user, follow these steps:
                    Personality: Analyze user personality and understand his likes and dislikes.
                    
                    Previous purchases: Determine the taste and user preferrences.
                
                    Match Choices: Compare the user's preferences with the provided choices.
                
                    Recommend Product: Select the best {no_of_products} product from the choices that best aligns with the user preferences. 
                Note: Just give me the recommended product and reasoning in following json format. 
                {{
                    "product 1": {{
                            "product name": "",
                            "image link": "",
                            "description": "",
                            "reason": ""
                    }}
                }}
            """
    instruct = """You are an advance recommendation system. Recommend top best product among the choices."""
    recommendation = callOpenAI(template, instruct)
    recommendation_object['top_best'] = recommendation
    if verbose:
        print("Info: Overall Top Best done!")
    
    if verbose:
        print("Info: Completed getRecommendation successfully")

        print("Here is the final result recommendaton object!!")
        print(recommendation_object)
        
    return recommendation_object

def getProductDetails(id):
    global collection
    details = collection.get(id)
    return details

def getProductDetailsByName(name):
    global collection

    results = collection.query(
        query_texts = [name],
        n_results = 1,
        include = [ "metadatas", "documents"]
    )
    return results