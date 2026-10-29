
"""
question_bank.py
Domain-specific interview questions with 100 questions per domain.
Questions are selected randomly and returned in a sequence.
"""

import random


def _build_questions(topics, prompts):
    """Generate 100 distinct question prompts from 10 topics x 10 styles."""
    questions = []
    for topic in topics:
        for prompt in prompts:
            questions.append(prompt.format(topic=topic))
    return list(dict.fromkeys(questions))


# ============================================================
# AIML: 100 QUESTIONS
# ============================================================

TECHNICAL_QUESTIONS = {
    "AIML": _build_questions(
        [
            "supervised and unsupervised learning",
            "bias, variance, and generalization",
            "feature engineering and feature selection",
            "model evaluation and cross-validation",
            "neural networks and backpropagation",
            "convolutional neural networks",
            "natural language processing and embeddings",
            "transformers and attention mechanisms",
            "model deployment and monitoring",
            "data quality, leakage, and class imbalance",
        ],
        [
            "Explain the key ideas behind {topic} and give a practical example.",
            "When would you use {topic} in a real-world AI/ML project?",
            "What common mistakes do beginners make with {topic}, and how would you avoid them?",
            "How would you evaluate whether an approach to {topic} is working well?",
            "Describe a project scenario where {topic} would be especially important.",
            "What trade-offs should an engineer consider when working with {topic}?",
            "How can you debug a problem related to {topic} in a machine-learning pipeline?",
            "How does {topic} affect the reliability of a deployed model?",
            "What metrics or evidence would you use to assess {topic}?",
            "Explain {topic} to a non-technical stakeholder and describe its impact.",
        ],
    ),

    # ========================================================
    # WEB DEVELOPMENT: 100 QUESTIONS
    # ========================================================

    "Web Development": _build_questions(
        [
            "semantic HTML and accessible forms",
            "CSS layout, Flexbox, and Grid",
            "JavaScript scope, closures, and promises",
            "React components, props, and state",
            "React hooks and component lifecycle",
            "REST APIs, HTTP methods, and status codes",
            "authentication, authorization, and sessions",
            "database queries, indexes, and transactions",
            "web security, CORS, and input validation",
            "performance, caching, and responsive design",
        ],
        [
            "Explain the core concepts of {topic} and give a practical example.",
            "How would you apply {topic} when building a production web application?",
            "What mistakes commonly occur with {topic}, and how would you prevent them?",
            "How would you test and debug a problem involving {topic}?",
            "Describe a realistic project requirement that would make {topic} important.",
            "What are the main trade-offs when choosing an approach to {topic}?",
            "How does {topic} affect user experience, maintainability, or performance?",
            "How would you explain {topic} to a junior developer joining your team?",
            "What security or reliability concerns should you consider with {topic}?",
            "How would you improve an existing application that has problems with {topic}?",
        ],
    ),

    # ========================================================
    # DATA SCIENCE: 100 QUESTIONS
    # ========================================================

    "Data Science": _build_questions(
        [
            "data cleaning and missing values",
            "exploratory data analysis",
            "probability distributions and sampling",
            "hypothesis testing and p-values",
            "regression and classification",
            "feature engineering and selection",
            "model validation and performance metrics",
            "SQL joins, grouping, and window functions",
            "Pandas, NumPy, and data transformations",
            "visualization, storytelling, and communicating insights",
        ],
        [
            "Explain the key concepts of {topic} with an example from a real dataset.",
            "How would you use {topic} to solve a business problem?",
            "What errors or misleading conclusions can arise when working with {topic}?",
            "How would you validate the results of an analysis involving {topic}?",
            "Describe a project where {topic} would be a critical step.",
            "Which tools, techniques, or metrics are useful for {topic}, and why?",
            "How would you investigate an unexpected result related to {topic}?",
            "What assumptions should you check before applying {topic}?",
            "How would you explain findings about {topic} to a non-technical audience?",
            "How can you make a workflow involving {topic} more reproducible and reliable?",
        ],
    ),
}


# ============================================================
# HR: 100 QUESTIONS
# ============================================================

HR_TOPICS = [
    "introducing yourself and summarizing your background",
    "identifying your strengths and development areas",
    "explaining why you want this role",
    "setting career goals for the next five years",
    "working through a disagreement with a teammate",
    "handling pressure and competing deadlines",
    "learning from a mistake or failed attempt",
    "demonstrating leadership without formal authority",
    "receiving and applying constructive feedback",
    "adapting when priorities or requirements change",
]

HR_PROMPTS = [
    "Describe how you would approach {topic}, using a specific example where possible.",
    "Tell me about a real situation that demonstrates your approach to {topic}.",
    "What did you learn from an experience involving {topic}?",
    "How would a previous teammate or manager describe your approach to {topic}?",
    "What challenges can arise with {topic}, and how would you handle them?",
    "How do you measure whether you handled {topic} successfully?",
    "Describe a time when {topic} required you to make a difficult decision.",
    "What would you do differently next time you face a situation involving {topic}?",
    "How would you handle a scenario where {topic} becomes difficult under time pressure?",
    "What specific actions demonstrate your ability to manage {topic} effectively?",
]

HR_QUESTIONS = _build_questions(HR_TOPICS, HR_PROMPTS)

# HR can also be selected directly from the domain dropdown.
TECHNICAL_QUESTIONS["HR"] = HR_QUESTIONS


# ============================================================
# COMPANY-WISE CAMPUS PLACEMENT QUESTION BANK
# ============================================================

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
            "TCS has a strict code of conduct. How do you feel about that?",
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
            "Explain the SDLC phases.",
            "What is the difference between process and thread?",
            "Explain SQL joins with examples.",
            "What is exception handling? Give an example.",
        ],
        "hr": [
            "Why Infosys and not another IT company?",
            "How do you handle conflicting opinions in a team?",
            "How do you keep your technical skills updated?",
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
            "If PAPER is coded as RCTGT, how is PENCIL coded?",
            "A father is 3 times as old as his son. After 12 years he will be twice as old. Find their current ages.",
        ],
        "technical": [
            "Explain the difference between SQL and NoSQL databases.",
            "What is Agile methodology? How is it different from Waterfall?",
            "What is an API and how does it work?",
        ],
        "hr": [
            "Give an example of when you adapted to a big change.",
            "Why should Accenture hire you specifically?",
        ],
    },

    "Amazon": {
        "aptitude": [
            "Estimate how many tennis balls fit inside a school bus.",
            "A warehouse processes 500 orders in 8 hours. What is the average processing rate per hour?",
        ],
        "technical": [
            "Explain how a hash map works internally.",
            "Design a simplified shopping cart system. What tables or entities would you use?",
            "What is the difference between an array and a linked list?",
        ],
        "hr": [
            "Tell me about a time you disagreed with your manager.",
            "Describe a situation where you made a decision without complete information.",
            "Tell me about a time you took ownership of a problem outside your role.",
        ],
    },

    "Google": {
        "aptitude": [
            "You have 9 balls, one heavier than the rest. Using a balance scale twice, how do you find it?",
            "How would you estimate the number of search queries Google handles per second?",
        ],
        "technical": [
            "Explain how you would design a URL shortening service.",
            "What is the difference between BFS and DFS?",
            "How would you detect a cycle in a linked list?",
        ],
        "hr": [
            "Tell me about a project where you faced technical ambiguity.",
            "Describe a time you received difficult feedback.",
        ],
    },

    "Microsoft": {
        "aptitude": [
            "A digital clock shows the time 04:15. When will its hour and minute hands overlap next?",
            "Estimate how many piano tuners are in a city of 5 million people.",
        ],
        "technical": [
            "Explain the difference between a compiler and an interpreter.",
            "How would you design a scalable notification system?",
            "What is multithreading, and what problems can arise from it?",
        ],
        "hr": [
            "Tell me about a time you worked with ambiguous requirements.",
            "Describe a project you're proud of and your specific role in it.",
        ],
    },
}

COMPANY_LIST = list(COMPANY_QUESTION_BANK.keys())


# ============================================================
# QUESTION SELECTION FUNCTIONS
# ============================================================

def _sample_questions(bank, n):
    """Select random questions without repeating within the selected set."""
    if not isinstance(n, int) or n <= 0:
        return []

    return random.sample(bank, min(n, len(bank)))


def get_hr_questions(n=3):
    """Return a random selection of HR questions."""
    return _sample_questions(HR_QUESTIONS, n)


def get_technical_questions(domain, n=3):
    """Return random questions from the selected domain."""
    if not domain:
        raise ValueError("An interview domain must be selected.")

    aliases = {
        "aiml": "AIML",
        "ai/ml": "AIML",
        "artificial intelligence and machine learning": "AIML",
        "web development": "Web Development",
        "web dev": "Web Development",
        "data science": "Data Science",
        "hr": "HR",
        "human resources": "HR",
    }

    canonical_domain = aliases.get(domain.strip().casefold())

    if canonical_domain is None:
        raise ValueError(
            f"Unsupported interview domain: {domain}. "
            "Choose AIML, Web Development, Data Science, or HR."
        )

    return _sample_questions(TECHNICAL_QUESTIONS[canonical_domain], n)


def get_company_questions(
    company: str,
    num_aptitude=2,
    num_technical=2,
    num_hr=2,
) -> list:
    """Return randomized aptitude, technical, and HR questions."""
    if not company:
        return []

    company_key = next(
        (
            name for name in COMPANY_QUESTION_BANK
            if name.casefold() == company.strip().casefold()
        ),
        None,
    )

    if company_key is None:
        return []

    bank = COMPANY_QUESTION_BANK[company_key]

    questions = []
    questions.extend(_sample_questions(bank["aptitude"], num_aptitude))
    questions.extend(_sample_questions(bank["technical"], num_technical))
    questions.extend(_sample_questions(bank["hr"], num_hr))

    return questions
