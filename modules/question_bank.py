"""
question_bank.py
------------------
Static question banks:
 1. HR_QUESTIONS            - generic behavioral questions
 2. TECHNICAL_QUESTIONS     - per technical domain (AIML, Web Dev, Data Science)
 3. COMPANY_QUESTION_BANK   - per-company campus placement questions, each split
                              into aptitude / technical / hr rounds, covering the
                              companies most commonly recruiting on Indian campuses.
"""

HR_QUESTIONS = [
    "Tell me about yourself.",
    "What are your greatest strengths and weaknesses?",
    "Why do you want to work with our company?",
    "Where do you see yourself in five years?",
    "Describe a time you faced conflict in a team and how you resolved it.",
    "Why should we hire you over other candidates?",
    "Tell me about a challenge you overcame.",
    "How do you handle pressure and tight deadlines?",
]

TECHNICAL_QUESTIONS = {
    "AIML": [
        "Explain the bias-variance tradeoff in machine learning.",
        "What is the difference between supervised and unsupervised learning?",
        "How does a convolutional neural network differ from a fully connected network?",
        "Explain overfitting and how you would prevent it.",
        "What is the purpose of an activation function in a neural network?",
        "Explain the difference between precision and recall.",
    ],
    "Web Development": [
        "Explain the difference between REST and GraphQL APIs.",
        "What is the virtual DOM and why does React use it?",
        "How would you optimize a website's page load speed?",
        "Explain the concept of middleware in Express.js or Django.",
        "What is CORS and why does it matter for web apps?",
        "Describe how you'd design a scalable authentication system.",
    ],
    "Data Science": [
        "What is the Central Limit Theorem and why does it matter?",
        "How do you handle missing data in a dataset?",
        "Explain the difference between Type I and Type II errors.",
        "What is feature engineering and why is it important?",
        "How would you evaluate a classification model's performance?",
        "Explain the difference between correlation and causation.",
    ],
    "HR": [
        "How do you evaluate a candidate's cultural fit?",
        "Describe your approach to resolving workplace conflict.",
        "How do you keep a team motivated during a difficult project?",
    ],
}

# ---------------------------------------------------------------------------
# Company-wise campus placement question bank.
# Each company has three rounds: aptitude, technical, hr -- matching the
# standard Indian campus placement drive structure.
# ---------------------------------------------------------------------------
COMPANY_QUESTION_BANK = {
    "TCS": {
        "aptitude": [
            "A train 150m long crosses a platform of 250m in 20 seconds. Find its speed.",
            "If the ratio of ages of A and B is 3:5 and after 6 years the ratio becomes 4:6, find their present ages.",
            "Find the next number in the series: 2, 6, 12, 20, 30, ?",
            "A can complete a work in 12 days and B in 18 days. In how many days will they finish it together?",
        ],
        "technical": [
            "What is the difference between a stack and a queue?",
            "Explain normalization in DBMS with an example.",
            "What are the OOP concepts? Explain each briefly.",
            "Write pseudocode to reverse a linked list.",
        ],
        "hr": [
            "Why do you want to join TCS?",
            "Are you willing to relocate for this role?",
            "TCS has a strict code of conduct -- how do you feel about that?",
        ],
    },
    "Infosys": {
        "aptitude": [
            "A shopkeeper marks up goods by 40% and gives a discount of 10%. Find his profit percentage.",
            "Find the odd one out: 3, 5, 7, 9, 11.",
            "If a code language assigns CAT = 3120, what does DOG equal?",
            "Two pipes fill a tank in 20 and 30 minutes respectively. How long will both take together?",
        ],
        "technical": [
            "Explain the SDLC (Software Development Life Cycle) phases.",
            "What is the difference between process and thread?",
            "Explain SQL joins with examples.",
            "What is exception handling? Give an example in any language you know.",
        ],
        "hr": [
            "Why Infosys and not another IT company?",
            "How do you handle working in a team with conflicting opinions?",
            "Infosys emphasizes continuous learning -- how do you keep your skills updated?",
        ],
    },
    "Wipro": {
        "aptitude": [
            "A sum of money doubles itself in 8 years at simple interest. Find the rate of interest.",
            "In a class, 60% are boys. If there are 24 girls, how many students are there in total?",
            "Find the missing number: 5, 11, 23, 47, ?",
        ],
        "technical": [
            "What is polymorphism? Explain with a real-world example.",
            "Explain the difference between primary key and foreign key.",
            "What is the time complexity of binary search and why?",
        ],
        "hr": [
            "What do you know about Wipro's business verticals?",
            "Describe a situation where you had to learn something new quickly.",
        ],
    },
    "Accenture": {
        "aptitude": [
            "A car travels 60 km in 45 minutes. What is its speed in km/hr?",
            "If 'PAPER' is coded as 'RCTGT', how is 'PENCIL' coded?",
            "A father is 3 times as old as his son. After 12 years he will be twice as old. Find their current ages.",
        ],
        "technical": [
            "Explain the difference between SQL and NoSQL databases.",
            "What is Agile methodology? How is it different from Waterfall?",
            "What is an API and how does it work?",
        ],
        "hr": [
            "Accenture values adaptability -- give an example of when you adapted to a big change.",
            "Why should Accenture hire you specifically?",
        ],
    },
    "Amazon": {
        "aptitude": [
            "Estimate how many tennis balls fit inside a school bus (structured estimation question).",
            "A warehouse processes 500 orders in 8 hours. What is the average processing rate per hour?",
        ],
        "technical": [
            "Explain how a hash map works internally.",
            "Design a simplified version of Amazon's shopping cart system -- what tables/entities would you use?",
            "What is the difference between an array and a linked list, and when would you choose each?",
        ],
        "hr": [
            "Tell me about a time you disagreed with your manager. What did you do?",
            "Describe a situation where you had to make a decision without complete information.",
            "This is a leadership-principle style question: tell me about a time you took ownership of a problem outside your role.",
        ],
    },
    "Google": {
        "aptitude": [
            "You have 9 balls, one heavier than the rest. Using a balance scale twice, how do you find it?",
            "How would you estimate the number of search queries Google handles per second?",
        ],
        "technical": [
            "Explain how you would design a URL shortening service.",
            "What is the difference between BFS and DFS, and when would you use each?",
            "How would you detect a cycle in a linked list?",
        ],
        "hr": [
            "Tell me about a project where you had significant technical ambiguity. How did you proceed?",
            "Describe a time you received difficult feedback. How did you respond?",
        ],
    },
    "Microsoft": {
        "aptitude": [
            "A digital clock shows the time 04:15. How many minutes until the hour and minute hands overlap again?",
            "Estimate how many piano tuners are in a city of 5 million people.",
        ],
        "technical": [
            "Explain the difference between a compiler and an interpreter.",
            "How would you design a scalable notification system?",
            "What is multithreading, and what problems can arise from it?",
        ],
        "hr": [
            "Tell me about a time you had to work with an ambiguous set of requirements.",
            "Describe a project you're proud of and your specific role in it.",
        ],
    },
}

COMPANY_LIST = list(COMPANY_QUESTION_BANK.keys())


def get_hr_questions(n=3):
    return HR_QUESTIONS[:n]


def get_technical_questions(domain, n=3):
    return TECHNICAL_QUESTIONS.get(domain, TECHNICAL_QUESTIONS["AIML"])[:n]


def get_company_questions(company: str, num_aptitude=2, num_technical=2, num_hr=2) -> list:
    """Returns a mixed-round question list for one company's placement drive."""
    bank = COMPANY_QUESTION_BANK.get(company)
    if not bank:
        return []
    questions = []
    questions.extend(bank["aptitude"][:num_aptitude])
    questions.extend(bank["technical"][:num_technical])
    questions.extend(bank["hr"][:num_hr])
    return questions
