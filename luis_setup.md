# Setting up Azure Language Understanding (LUIS)

After creating your LUIS resource in Azure, follow these steps to set up a language model for your career guidance chatbot:

## 1. Create a LUIS App

1. Go to the [LUIS portal](https://www.luis.ai/) and sign in with your Azure account
2. Click "New app" and fill in the details:
   - Name: CareerGuidanceChatbot
   - Culture: English
   - Description: A chatbot that suggests career paths based on skills
3. Click "Done"

## 2. Create Intents

Intents represent the user's intention or goal. Create the following intents:

### SkillsInput Intent
1. Click "Build" in the top menu, then "Intents" in the left menu
2. Click "Create" to create a new intent
3. Name it "SkillsInput"
4. Add example utterances:
   - "I know Python, data analysis, and machine learning"
   - "My skills are web development and UI design"
   - "I'm good at cybersecurity and network administration"
   - "I have experience with cloud computing and DevOps"
   - "I can do mobile app development and game design"
   - "My strengths are database management and SQL"
   - "I'm skilled in artificial intelligence and deep learning"
   - "I know JavaScript, HTML, and CSS"
   - "I'm familiar with project management and agile methodologies"
   - "I have skills in graphic design and UX/UI"

### GetCareerDetails Intent
1. Create another intent named "GetCareerDetails"
2. Add example utterances:
   - "Tell me more about data science"
   - "What skills do I need for software engineering?"
   - "I want to learn about cybersecurity careers"
   - "Give me details about artificial intelligence jobs"
   - "What does a UX designer do?"
   - "Tell me about web development careers"
   - "What is machine learning as a career?"
   - "Information about cloud computing jobs"
   - "What skills are needed for mobile development?"
   - "Tell me about game development careers"

### RecommendSkills Intent
1. Create another intent named "RecommendSkills"
2. Add example utterances:
   - "What skills should I learn next?"
   - "Recommend additional skills for data science"
   - "What else should I learn for web development?"
   - "Suggest skills to complement my knowledge of Python"
   - "What skills are in demand for AI jobs?"
   - "What should I learn after mastering JavaScript?"
   - "Recommend skills to improve my employability"
   - "What skills go well with UX design?"
   - "Suggest complementary skills for cybersecurity"
   - "What else should I know for cloud computing?"

## 3. Create Entities

Entities are important data points you want to extract from user input:

### Skills Entity
1. Click "Entities" in the left menu
2. Click "Create" to create a new entity
3. Name it "Skills"
4. Entity type: List
5. Add the following values (with synonyms):
   - Python (synonyms: python programming, python coding)
   - JavaScript (synonyms: JS, javascript coding)
   - Machine Learning (synonyms: ML, machine learning algorithms)
   - Data Analysis (synonyms: data analytics, analyzing data)
   - Web Development (synonyms: web dev, website development)
   - Mobile Development (synonyms: mobile apps, app development)
   - Cloud Computing (synonyms: cloud, AWS, Azure, GCP)
   - Cybersecurity (synonyms: security, information security)
   - UI/UX Design (synonyms: user interface, user experience)
   - Database Management (synonyms: SQL, database admin)

### CareerPath Entity
1. Create another entity named "CareerPath"
2. Entity type: List
3. Add the following values (with synonyms):
   - Data Science (synonyms: data scientist, analytics)
   - Software Development (synonyms: software engineering, programming)
   - Artificial Intelligence (synonyms: AI, machine learning engineer)
   - Web Development (synonyms: web developer, frontend, backend)
   - Cybersecurity (synonyms: security analyst, security engineer)
   - UX/UI Design (synonyms: user experience, interface design)
   - Mobile Development (synonyms: app developer, iOS, Android)
   - Cloud Engineering (synonyms: cloud architect, DevOps)
   - Game Development (synonyms: game designer, game programmer)
   - Database Administration (synonyms: DBA, database engineer)

## 4. Label Entities in Utterances

1. Go back to each intent and label the entities in your example utterances
2. For example, in "I know Python, data analysis, and machine learning", label:
   - "Python" as Skills
   - "data analysis" as Skills
   - "machine learning" as Skills

## 5. Train and Test the Model

1. Click "Train" in the top right to train your model
2. Once training is complete, click "Test" to test your model with sample utterances
3. Try utterances like "I know Python and machine learning" to see if it correctly identifies the intent and entities

## 6. Publish the Model

1. Click "Publish" in the top menu
2. Select "Production slot"
3. Click "Done"
4. Note the Endpoint URL and Subscription Key for use in your application

## 7. Get Prediction URL

After publishing, you'll get a Prediction URL that looks like:
```
https://{your-region}.api.cognitive.microsoft.com/luis/prediction/v3.0/apps/{app-id}/slots/production/predict?subscription-key={subscription-key}&verbose=true&show-all-intents=true&log=true&query=YOUR_QUERY_HERE
```

Save this URL for use in your application.
