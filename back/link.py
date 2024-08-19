import requests
from requests.auth import HTTPBasicAuth
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
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

# Function to scrape LinkedIn and add a user to Neo4j
def linkedin_scraper_and_add(profile_url, email, password):
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
        # Navigate to LinkedIn login page
        driver.get('https://www.linkedin.com/login')
        time.sleep(2)  # Let the page load

        # Enter email
        email_input = driver.find_element(By.ID, 'username')
        email_input.send_keys(email)

        # Enter password
        password_input = driver.find_element(By.ID, 'password')
        password_input.send_keys(password)
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

# Usage example
profile_url = 'https://www.linkedin.com/in/belhajomar/'
email = 'khaled.tebourbi69@gmail.com'
password = 'vWjHQ6gbk!@YtL6'

profile_data = linkedin_scraper_and_add(profile_url, email, password)
if profile_data:
    print(profile_data)
    ndomaine = profile_data['domaine']
    credly_profile_url = f"https://www.credly.com/earner/dashboard#gs_q={ndomaine.replace(' ', '+')}"
    credly_email = 'mohamedkhaled.tebourbi@esprit.tn'
    credly_password = '4gCd!nnvx3j_6C2'
    neo4j_url = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "khaledAZE123"

    # Scrape skills
    skills = selenium_credly_scraper(credly_profile_url, credly_email, credly_password)

    # Update Neo4j with the scraped skills
    if skills:
        update_neo4j_with_skills(neo4j_url, neo4j_user, neo4j_password, ndomaine, skills)
        for skill in skills:
            print(f"Skill: {skill}")
    else:
        print("Failed to scrape the skills.")
else:
    print("Failed to scrape the profile.")
