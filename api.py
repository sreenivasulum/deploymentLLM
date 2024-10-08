# Building personalized RecSys using LLMs Api Layer
"""Routes:
/twitter
    <= twitter handle | username
    => tweets, personality
/getRecommendations
    <= selection object
    => recommendation object

selection object : 
{
    domain_name : [
        {
            "name":"product_name"
        }
    ],
    "twitter": "username"

}

recommendation object : 
{
    "Top Best Recommendation": {
			"product name": "product name",
			"image_url": "image_url",
            "explanation": ""
		}
    "Top 5 Best Recommendations": [
			{
			"product name": "product name",
			"image_url": "image_url",
                "explanation": ""
			},
			{
				"product name": "product name",
				"image_url": "image_url",
                "explanation": ""
			},
			{
				"product name": "product name",
				"image_url": "image_url",
                "explanation": ""
			},
			{
				"product name": "product name",
				"image_url": "image_url",
                "explanation": ""
			},{
				"product name": "product name",
				"image_url": "image_url",
                "explanation": ""
			}
		],
    "In-domain predictions": {
        domain_name : [
            {
				"product name": "product name",
				"image_url": "image_url",
                "explanation": ""
			}
        ]
    },
    "Cross-domain predictions": {
        domain_name : [
            {
				"product name": "product name",
				"image_url": "image_url",
                "explanation": ""
			}
        ]
    }
}

/getProducts
    <= domain_name
    => list of products
    [
        {
            "product_name": "",
            "description:: "",
            "link":""
        }
    ]
"""

# libraries
from flask import Flask, request 
from flask_cors import CORS
import os
import app1



## Routes ::>
app = Flask(__name__)
CORS(app)

@app.route('/',methods = ['GET','POST'])
def hello_world():
    return 'Hello World'

@app.route('/tweets',methods = ['GET','POST'])
def tweets():
    username = request.args.get('username') 
    ## 
    userid = app1.getUserId(username)
    tweets = app1.getTweets(userid)
    return tweets

@app.route('/personality',methods = ['GET','POST'])
def personality():
    personality = app1.getPersonality(username)
    return personality


@app.route('/getRecommendation',methods = ['GET','POST'])
def getRecommendation():
    # input => selection obj
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

    personality = """Based on the given Twitter posts, the user appears to be deeply involved in the academic and practical applications of language models and generative AI (artificial intelligence). Their interests seem to primarily revolve around the enhancement and personalization of Large Language Models (LLMs), as evidenced by their discussions, retweets, and involvement in organizing workshops in this domain.

        **Likes and Interests:**
        1. **Artificial Intelligence Research**: The user is interested in the exploration and development of LLMs, focusing on how these models handle specific queries and how personal biases can be incorporated or mitigated.
        2. **Academic Publications**: They show an affinity for sharing and promoting new research findings, as indicated by their posts about papers featured in EMNLP and their organization of related workshops.
        3. **Community Engagement**: The user enjoys engaging with the AI research community, evident from their updates on workshops and calls for submissions in the field. They seem to value collaborative efforts and interactions within the community.

        **Dislikes and Concerns:**
        1. **Bias in AI**: The user shows concern about biases in LLMs, as reflected in the discussion about personas affecting LLM behavior. They appear to advocate for awareness and solutions to address these intrinsic biases.
        2. **Ownership and Intellectual Property Rights in AI**: They retweeted concerns regarding how creations by entities like the NYT can maintain visibility and ownership amidst the rise of new AI-driven search engines.

        **Domain Expertise and Involvement:**
        - The user not only follows advancements in AI but actively contributes to its development through academic papers and organizing industry-specific workshops. They appear to be recognized in their field, collaborating with other experts and managing events that foster discussion on technical, philosophical, and legal aspects of AI.

        **Engagement Style:**
        - The user’s tweets are informational and professional, focused on sharing valuable insights, research findings, and opportunities for collaboration. They effectively use their platform to promote academic events and encourage active participation from their followers in the broader AI discussions.

        **Networking and Community Building:**
        - The user is proactive in building and nurturing a professional network, indicated by their mentions of and interactions with other professionals across various capacities in the AI field. They seem to play a pivotal role in organizing events that bring experts together, hence facilitating a richer exchange of ideas.

        Overall, this personality profile suggests a highly intellectual, engaged, and proactive individual who is dedicated to advancing the field of artificial intelligence through active research, community engagement, and thoughtful discussion on critical issues like bias and personalization in AI technologies.
    """
    recommend = app1.getRecommendation(selection,personality)
   
    return recommend


# main driver function
if __name__ == '__main__':

    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(debug=True)
