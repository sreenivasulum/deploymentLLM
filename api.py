from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue
from dotenv import load_dotenv
import time
from flask_cors import CORS
import os
import app1

app = Flask(__name__)
CORS(app)
load_dotenv()
# Connect to Redis
redis_conn = Redis.from_url(os.getenv('REDIS_URL'))
q = Queue(connection=redis_conn)

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'Hello World'

@app.route('/start-task', methods=['POST'])
def start_task():
    data = request.get_json()
    job = q.enqueue(app1.background_task, data['n'])
    return jsonify({'job_id': job.get_id()})

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

    
    if not selection or not personality:
        return jsonify({"error": "Selection and personality are required"}), 400

    # Enqueue the recommendation task
    job1 = q.enqueue(app1.getRecommendation, selection, personality)

    #return job1.result
   
    return jsonify({'job_id': job1.get_id()})


@app.route('/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
    job = q.fetch_job(job_id)
    if job.is_finished:
        return jsonify({'status': 'finished', 'result': job.result})
    elif job.is_failed:
        return jsonify({'status': 'failed'})
    else:
        return jsonify({'status': 'in progress'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
