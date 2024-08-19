from flask import Flask, render_template, request, redirect, url_for
from neo4j import GraphDatabase
from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from flask_cors import CORS 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
from neo4j import GraphDatabase
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, request, jsonify
from neo4j import GraphDatabase
import jwt
import datetime






app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for /api routes


# Configuration de la connexion à Neo4j
neo4j_url = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "khaledAZE123"

driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))

@app.route("/")
def index():
    

    result = []
    with driver.session() as session:
        result = session.run("MATCH (u:User) RETURN u.domaine AS domaine, u.name AS name, u.id AS id, u.url AS url, u.email AS email, u.pays AS pays, u.password AS password")
        result = [dict(record) for record in result]
    return render_template('index.html', result=result)
@app.route("/domaine")
def index2():
    result = []
    with driver.session() as session:
        # Récupérer toutes les compétences disponibles
        result = session.run("MATCH (s:Skill) RETURN s.id_ski AS id, s.nski AS nski, s.typee AS typee")
        resulte = session.run("MATCH (d:Domaine)-[:HAS_SKILL]->(s:Skill) "
            "RETURN d.ndomaine AS ndomaine, d.description AS description, collect(s.nski) AS skills")
        result = [dict(record) for record in result]
        resulte = [dict(record) for record in resulte]
    return render_template('inde.html', result=result, resulte=resulte)
@app.route("/skills")
def index22():
    result = []
    with driver.session() as session:
        # Récupérer toutes les compétences disponibles
        result = session.run("MATCH (s:Skill) RETURN s.id_ski AS id, s.nski AS nski, s.typee AS typee")
        
        result = [dict(record) for record in result]
       
    return render_template('ind.html', result=result)
@app.route("/ajouter_domaine", methods=["POST"])
def ajouter_domaine():
    ndomaine = request.form.get("ndomaine")
    description = request.form.get("description")
    skills = request.form.getlist("skills")  # Récupère une liste des compétences sélectionnées
    
    with driver.session() as session:
        # Créer le domaine
        result = session.run("CREATE (d:Domaine {ndomaine: $ndomaine, description: $description}) RETURN d",
                             ndomaine=ndomaine, description=description)
        domaine_node = result.single()["d"]
        
       
        # Ajouter les nouvelles relations HAS_SKILL avec les compétences sélectionnées
        for skill_name in skills:
            session.run("MATCH (d:Domaine {ndomaine: $ndomaine}), (s:Skill {nski: $nski}) "
                        "CREATE (d)-[:HAS_SKILL]->(s)",
                        ndomaine=ndomaine, nski=skill_name)
    
    return redirect(url_for('index2'))
@app.route("/supprimer_domaine/<ndomaine>", methods=["POST"])
def supprimer_domaine(ndomaine):
    with driver.session() as session:
        # Supprimer le domaine et ses relations HAS_SKILL
        session.run("MATCH (d:Domaine {ndomaine: $ndomaine}) "
                    "OPTIONAL MATCH (d)-[r:HAS_SKILL]->() "
                    "DELETE d, r",
                    ndomaine=ndomaine)
    
    return redirect(url_for('index2')) 

@app.route("/ajouter_skill", methods=["POST"])
def ajouter_skill():
    nski = request.form['nski']
    typee = request.form['typee']
    
    with driver.session() as session:
        # Créer le skill
        result = session.run(
            "CREATE (s:Skill {nski: $nski, typee: $typee}) RETURN s",
            nski=nski, typee=typee)
        skill_node = result.single()["s"]
        return redirect(url_for('index22'))

@app.route("/supprimer_skill/<nski>", methods=["POST"])
def supprimer_skill(nski):
    with driver.session() as session:
        # Supprimer le skill et ses relations
        session.run("MATCH (s:Skill {nski: $nski}) "
                    "OPTIONAL MATCH (s)-[r]-() "
                    "DELETE s, r",
                    nski=nski)
    
    return redirect(url_for('index22'))
@app.route("/modifier_domaine", methods=["POST"])
def modifier_domaine():
    ndomaine = request.form.get("ndomaine")
    description = request.form.get("description")
    skills = request.form.getlist("skills")

    with driver.session() as session:
        # Mettre à jour la description du domaine
        session.run("MATCH (d:Domaine {ndomaine: $ndomaine}) SET d.description = $description",
                    ndomaine=ndomaine, description=description)
        
        
        
        # Ajouter les nouvelles relations HAS_SKILL avec les compétences sélectionnées
        for skill_name in skills:
            session.run("MATCH (d:Domaine {ndomaine: $ndomaine}), (s:Skill {nski: $nski}) "
                        "CREATE (d)-[:HAS_SKILL]->(s)",
                        ndomaine=ndomaine, nski=skill_name)
    
    return redirect(url_for('index2'))


neo4j_url = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "khaledAZE123"

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", neo4j_password))

def get_next_id(tx):
    result = tx.run("MATCH (u:User) RETURN max(u.id) as id")
    record = result.single()
    if record and record["id"]:
        return int(record["id"]) + 1
    return 1

@app.route('/api/users', methods=['POST'])
def create_user():
    user_data = request.json
    with driver.session() as session:
        new_id = session.execute_read(get_next_id)
        session.write_transaction(create_user_tx, new_id, user_data)
   

def create_user_tx(tx, user_id, user_data):
   tx.run("CREATE (u:User {id: $id, domaine: $domaine, name: $name, url: $url, pays: $pays, email: $email, password: $password})",
          id=user_id, domaine=user_data['domaine'], name=user_data['name'], url=user_data['url'], pays=user_data['pays'], email=user_data['email'], password=user_data['password'])



def verify_user(tx, email, password):
    result = tx.run("MATCH (u:User {email: $email, password: $password}) RETURN u.id AS user_id, u.url AS profile_url",
                    email=email, password=password)
    return result.single()

from flask import Flask, request, jsonify, make_response
CLIENT_ID = '77y94kzqjz6sfc'
CLIENT_SECRET = 'hGDWfDnZxC8SmXio'
AUTH_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
API_URL = 'https://api.linkedin.com/v2/me'

def get_access_token(CLIENT_ID, CLIENT_SECRET):
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    try:
        response = requests.post(AUTH_URL, data=data, auth=HTTPBasicAuth(CLIENT_ID,  CLIENT_SECRET))
        response.raise_for_status()  # Raises an HTTPError for bad response status
        response_data = response.json()
        access_token = 'AQXyJMSxvo4kfTmdZ-QDiigl9Km0pbvvE5Dk5StjjOv18fANrWub8G79LEO7W3VDJ6VfEg4CCLpV87JQYN3G_UA3_tl5gc4_3irLqSKC08sOUWfpbXFwJMoHGyFtw8i4tMuaUkn6x65w-Lzxk4X0cQeGZuiIFk7DaO9yNCMIvsFRkg1adLR667XbkfFfb5F-ca_gnxvVCgZY9uV9QHb5rQ_3RyTHvQWVZHShNZC99rdpYKJbAgQangm3ZBZSQk-BHYdx-35B0GphDkJr5zGB1d0Wegm5gPMqNPrC3RPE_uST3j2GjGfO1jIVYG_OY9JNTUTRcExgyM4BhfnNnh0rBb0wYuPNYg'
        if access_token:
            return access_token
        else:
            print("Access token not found in response:", response_data)
            return None
    except requests.exceptions.RequestException as e:
        print("Error fetching access token:", e)
        return None

def get_profile(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching profile data:", e)
        return None

# Main execution
access_token = 'AQXyJMSxvo4kfTmdZ-QDiigl9Km0pbvvE5Dk5StjjOv18fANrWub8G79LEO7W3VDJ6VfEg4CCLpV87JQYN3G_UA3_tl5gc4_3irLqSKC08sOUWfpbXFwJMoHGyFtw8i4tMuaUkn6x65w-Lzxk4X0cQeGZuiIFk7DaO9yNCMIvsFRkg1adLR667XbkfFfb5F-ca_gnxvVCgZY9uV9QHb5rQ_3RyTHvQWVZHShNZC99rdpYKJbAgQangm3ZBZSQk-BHYdx-35B0GphDkJr5zGB1d0Wegm5gPMqNPrC3RPE_uST3j2GjGfO1jIVYG_OY9JNTUTRcExgyM4BhfnNnh0rBb0wYuPNYg'
if access_token:
    profile_data = get_profile(access_token)
    if profile_data:
        print(profile_data)
    else:
        print("Failed to fetch profile data.")
else:
    print("Failed to obtain access token.")




@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        print("Received email:", email)
        print("Received password:", password)

        with driver.session() as session:
            user_record = session.execute_read(verify_user, email, password)

        if user_record:
            user_id = user_record['user_id']
            profile_url = f"{user_record['profile_url']}"

            print("User record found:", user_record)
            print("Profile URL:", profile_url)

            if access_token:
                emaill = 'khaled.tebourbi69@gmail.com'
                passwordl = 'vWjHQ6gbk!@YtL6'
                profile_data = linkedin_scraper_and_add(profile_url, emaill, passwordl)

                print("LinkedIn profile data:", profile_data)

                if profile_data:
                    ndomaine = profile_data['domaine']
                    credly_profile_url = f"https://www.credly.com/earner/dashboard#gs_q={ndomaine.replace(' ', '+')}"
                    credly_email = 'mohamedkhaled.tebourbi@esprit.tn'
                    credly_password = '4gCd!nnvx3j_6C2'
                    skills = selenium_credly_scraper(credly_profile_url, credly_email, credly_password)

                    print("Credly skills:", skills)

                    if skills:
                        update_neo4j_with_skills(neo4j_url, neo4j_user, neo4j_password, ndomaine, skills)
                        response = {
                            "success": True,
                            "user_id": user_id,
                            "profile_data": profile_data,
                            "skills": skills
                        }
                        print("Response:", response)
                        return make_response(jsonify(response), 200)
                    else:
                        response = {"success": True, "user_id": user_id, "profile_data": profile_data,"skills":skills, "message": "Failed to scrape skills from Credly"}
                        print("Response:", response)
                        return make_response(jsonify(response), 200)
                else:
                    response = {"success": True, "user_id": user_id, "message": "Failed to scrape LinkedIn profile"}
                    print("Response:", response)
                    return make_response(jsonify(response), 200)
            else:
                response = {"success": True, "user_id": user_id, "message": "Failed to obtain LinkedIn access token"}
                print("Response:", response)
                return make_response(jsonify(response), 200)
        else:
            response = {"success": False, "message": "Invalid email or password"}
            print("Response:", response)
            return make_response(jsonify(response), 401)

    except Exception as e:
        print("Error:", e)
        response = {"success": False, "message": "An error occurred"}
        return make_response(jsonify(response), 500)
        


@app.route('/api/user', methods=['GET'])
def get_user():
    # Vérifiez la présence du token dans les en-têtes de la requête
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({"success": False, "message": "Authorization token missing"}), 401

    # Authentifiez l'utilisateur et obtenez les informations de l'utilisateur
    user = login(token)
    
    if user:
        # Assurez-vous que la réponse contient les informations nécessaires
        user_info = {
            "email": user.get('email'),
            "profile_url": user.get('profile_url')
        }
        return jsonify(user_info)
    else:
        return jsonify({"success": False, "message": "User not authenticated"}), 401
@app.route('/api/profile', methods=['POST'])
def get_profile():
    try:
        data = request.json
        profile_url = data.get('profileUrl')
        email = data.get('email')
        password = data.get('password')

        if not profile_url or not email or not password:
            return jsonify({"success": False, "message": "Missing required parameters"}), 400

        # Appel de la fonction de scraping
        profile_data = linkedin_scraper_and_add(profile_url, email, password)

        if profile_data:
            return jsonify({"success": True, "name": profile_data['name'], "domaine": profile_data['domaine']})
        else:
            return jsonify({"success": False, "message": "Failed to scrape LinkedIn profile"}), 500

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    


@app.route('/api/login', methods=['OPTIONS'])
def options_login():
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    return response

   
CLIENT_ID = '77y94kzqjz6sfc'
CLIENT_SECRET = 'hGDWfDnZxC8SmXio'
AUTH_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
API_URL = 'https://api.linkedin.com/v2/me'

def get_access_token(CLIENT_ID, CLIENT_SECRET):
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    try:
        response = requests.post(AUTH_URL, data=data, auth=HTTPBasicAuth(CLIENT_ID,  CLIENT_SECRET))
        response.raise_for_status()  # Raises an HTTPError for bad response status
        response_data = response.json()
        access_token = 'AQXyJMSxvo4kfTmdZ-QDiigl9Km0pbvvE5Dk5StjjOv18fANrWub8G79LEO7W3VDJ6VfEg4CCLpV87JQYN3G_UA3_tl5gc4_3irLqSKC08sOUWfpbXFwJMoHGyFtw8i4tMuaUkn6x65w-Lzxk4X0cQeGZuiIFk7DaO9yNCMIvsFRkg1adLR667XbkfFfb5F-ca_gnxvVCgZY9uV9QHb5rQ_3RyTHvQWVZHShNZC99rdpYKJbAgQangm3ZBZSQk-BHYdx-35B0GphDkJr5zGB1d0Wegm5gPMqNPrC3RPE_uST3j2GjGfO1jIVYG_OY9JNTUTRcExgyM4BhfnNnh0rBb0wYuPNYg'
        if access_token:
            return access_token
        else:
            print("Access token not found in response:", response_data)
            return None
    except requests.exceptions.RequestException as e:
        print("Error fetching access token:", e)
        return None

def get_profile(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching profile data:", e)
        return None

# Main execution
access_token = 'AQXyJMSxvo4kfTmdZ-QDiigl9Km0pbvvE5Dk5StjjOv18fANrWub8G79LEO7W3VDJ6VfEg4CCLpV87JQYN3G_UA3_tl5gc4_3irLqSKC08sOUWfpbXFwJMoHGyFtw8i4tMuaUkn6x65w-Lzxk4X0cQeGZuiIFk7DaO9yNCMIvsFRkg1adLR667XbkfFfb5F-ca_gnxvVCgZY9uV9QHb5rQ_3RyTHvQWVZHShNZC99rdpYKJbAgQangm3ZBZSQk-BHYdx-35B0GphDkJr5zGB1d0Wegm5gPMqNPrC3RPE_uST3j2GjGfO1jIVYG_OY9JNTUTRcExgyM4BhfnNnh0rBb0wYuPNYg'
if access_token:
    profile_data = get_profile(access_token)
    if profile_data:
        print(profile_data)
    else:
        print("Failed to fetch profile data.")
else:
    print("Failed to obtain access token.")




# Function to scrape LinkedIn and add a user to Neo4j
def linkedin_scraper_and_add(profile_url, emaill, passwordl):
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-webgl")

    # Initialize the WebDriver
    service = Service('C:/Program Files (x86)/chromedriver.exe')  # Update the path to your ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to LinkedIn login page
        driver.get('https://www.linkedin.com/login')
        time.sleep(2)  # Let the page load

        # Enter email
        email_input = driver.find_element(By.ID, 'username')
        email_input.send_keys(emaill)

        # Enter password
        password_input = driver.find_element(By.ID, 'password')
        password_input.send_keys(passwordl)
        password_input.send_keys(Keys.RETURN)
        time.sleep(3)  # Let the login process complete

        # Navigate to the profile page
        driver.get(profile_url)
        time.sleep(3)  # Let the page load

        # Scroll to the bottom of the page to load all sections
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Extract profile information using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Example: Extract the name
        name_element = soup.find('h1', class_='text-heading-xlarge')
        name = name_element.get_text().strip() if name_element else 'N/A'

        # Example: Extract the headline
        domaine_element = soup.find('div', class_='text-body-medium')
        domaine = domaine_element.get_text().strip() if domaine_element else 'N/A'

        # Prepare profile data
        profile_data = {
            'name': name,
            'domaine': domaine,
        }

        # Add to Neo4j database
        add_to_neo4j(profile_data)

        return profile_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        driver.quit()



# Function to add a user to Neo4j
def add_to_neo4j(profile_data):
    neo4j_url = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "khaledAZE123"

    driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))

    with driver.session() as session:
        # Create user node with name and headline
        result = session.run(
            "CREATE (u:User {name: $name, domaine: $domaine}) RETURN u",
            name=profile_data['name'],
            domaine=profile_data['domaine']
        )

        for record in result:
            print(record)

# Function to scrape skills from Credly
def selenium_credly_scraper(profile_url, email, password):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-webgl")

    # Initialize the WebDriver
    service = Service('C:/Program Files (x86)/chromedriver.exe')  # Update the path to your ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the Credly login page
        driver.get('https://www.credly.com/users/sign_in')
        
        # Wait for the email input to be present
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'email'))
        )
        email_input.send_keys(email)

        # Enter password
        password_input = driver.find_element(By.NAME, 'password')
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        
        # Wait for the dashboard page to load
        WebDriverWait(driver, 10).until(
            EC.url_contains('dashboard')
        )
        
        # Navigate to the profile page
        driver.get(profile_url)
        
        # Wait for the skills section to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.c-global-search-results-category__item'))
        )
        
        # Extract the skills
        skill_elements = driver.find_elements(By.CSS_SELECTOR, '.c-global-search-results-item__label')
        
        # Collect and clean skills text
        skills = [skill.text.strip() for skill in skill_elements if skill.text.strip()]
        
        # Debugging: Print the number of skills found
        print(f"Number of skills found: {len(skills)}")
        
        return skills

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        driver.quit()
@app.route('/api/search', methods=['POST'])
def search_skills():
    data = request.get_json()
    query = data.get('query')

    profile_url = f"https://www.credly.com/earner/dashboard#gs_q={query.replace(' ', '+')}"
    email = 'mohamedkhaled.tebourbi@esprit.tn'
    password = '4gCd!nnvx3j_6C2'

    # Appeler la fonction selenium_credly_scraper pour extraire les compétences
    skillss = selenium_credly_scraper(profile_url, email, password)
    
    # Afficher toutes les compétences extraites avant le filtrage
    print(f"Skills before filtering: {skillss}")
    
    # Pas de filtrage, retournez directement toutes les compétences
    return jsonify(skillss)





# Function to update Neo4j with scraped skills
def update_neo4j_with_skills(neo4j_url, neo4j_user, neo4j_password, ndomaine, skills):
    # Initialize Neo4j driver
    driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))

    try:
        with driver.session() as session:
            # Create the domain if it does not exist
            session.run("MERGE (d:Domaine {ndomaine: $ndomaine})",
                        ndomaine=ndomaine)
            
            # Create skills nodes and relationships
            for skill_name in skills:
                print(f"Processing skill: {skill_name}")
                # Create skill node if it doesn't exist
                session.run("MERGE (s:Skill {nski: $nski})",
                            nski=skill_name)
                # Create relationship if it doesn't exist
                result = session.run("MATCH (d:Domaine {ndomaine: $ndomaine}), (s:Skill {nski: $nski}) "
                                     "MERGE (d)-[:HAS_SKILL]->(s) "
                                     "RETURN d, s",
                                     ndomaine=ndomaine, nski=skill_name)
                if result.single():
                    print(f"Relationship created for skill: {skill_name}")
                else:
                    print(f"Failed to create relationship for skill: {skill_name}")
    
    finally:
        driver.close()
        



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

