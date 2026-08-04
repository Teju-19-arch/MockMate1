"""
modules/technical/mock_provider.py
----------------------------------
Mock AI Question Provider implementation for offline testing, local dev,
and graceful fallback when Gemini API keys are absent or unavailable.
Provides 15 technical MCQs per domain/company.
"""

import logging
from typing import List, Dict, Any
from modules.technical.ai_provider import BaseAIProvider
from modules.technical.models import QuestionRequest

logger = logging.getLogger("modules.technical.mock_provider")

# Static fallback bank structured by Domain and Company with 15 questions each
MOCK_QUESTION_BANK = {
    "AIML": [
        {
            "question": "Which loss function is commonly used for multi-class classification tasks?",
            "options": {
                "A": "Mean Squared Error (MSE)",
                "B": "Categorical Cross-Entropy",
                "C": "Binary Cross-Entropy",
                "D": "Hinge Loss"
            },
            "correct_option": "B",
            "explanation": "Categorical Cross-Entropy measures the performance of a classification model whose output is a probability value between 0 and 1 across multiple discrete classes."
        },
        {
            "question": "What is the primary function of an Activation Function in a Neural Network?",
            "options": {
                "A": "To scale weights during backpropagation",
                "B": "To introduce non-linearity into the network",
                "C": "To prevent learning rate decay",
                "D": "To perform gradient clipping"
            },
            "correct_option": "B",
            "explanation": "Activation functions introduce non-linear properties to the network, allowing it to learn complex relationships in data."
        },
        {
            "question": "In Decision Trees, what metric measures the impurity or randomness of a dataset split?",
            "options": {
                "A": "Gini Impurity / Entropy",
                "B": "Euclidean Distance",
                "C": "Cosine Similarity",
                "D": "R-Squared Score"
            },
            "correct_option": "A",
            "explanation": "Gini Impurity and Information Gain (Entropy) quantify how homogeneous a node split is in a decision tree."
        },
        {
            "question": "What technique is specifically designed to prevent overfitting by randomly deactivating neurons during training?",
            "options": {
                "A": "Batch Normalization",
                "B": "Dropout",
                "C": "Gradient Descent",
                "D": "L1 Regularization"
            },
            "correct_option": "B",
            "explanation": "Dropout randomly sets a fraction of input units to 0 at each step during training time, preventing co-adaptation of features."
        },
        {
            "question": "Which evaluation metric is defined as True Positives divided by total predicted positives?",
            "options": {
                "A": "Recall",
                "B": "Precision",
                "C": "F1-Score",
                "D": "Specificity"
            },
            "correct_option": "B",
            "explanation": "Precision = TP / (TP + FP), focusing on the proportion of positive identifications that were actually correct."
        },
        {
            "question": "What does the learning rate hyperparameter control in Gradient Descent?",
            "options": {
                "A": "The step size taken towards the minimum of the loss function during optimization",
                "B": "The number of hidden layers in a deep neural network",
                "C": "The ratio of training data to test data",
                "D": "The initial weight value assigned to all neurons"
            },
            "correct_option": "A",
            "explanation": "Learning rate scales the magnitude of parameter updates with respect to the loss gradient."
        },
        {
            "question": "What is the primary indicator of Overfitting in a machine learning model?",
            "options": {
                "A": "High training error and high validation error",
                "B": "Low training accuracy and high test accuracy",
                "C": "High training accuracy but significantly lower validation/test accuracy",
                "D": "Equal performance across all datasets"
            },
            "correct_option": "C",
            "explanation": "Overfitting occurs when a model learns noise and detail in training data to the detriment of generalization on unseen test data."
        },
        {
            "question": "Which neural network architecture is best suited for spatial image data processing?",
            "options": {
                "A": "Recurrent Neural Network (RNN)",
                "B": "Convolutional Neural Network (CNN)",
                "C": "Multilayer Perceptron (MLP)",
                "D": "Autoencoder"
            },
            "correct_option": "B",
            "explanation": "CNNs preserve spatial hierarchies in 2D grid images via local receptive fields and weight sharing."
        },
        {
            "question": "Which neural network layer structure is specifically tailored for processing sequential or time-series data?",
            "options": {
                "A": "Dense Layer",
                "B": "Recurrent / LSTM / GRU Layer",
                "C": "Max Pooling Layer",
                "D": "Dropout Layer"
            },
            "correct_option": "B",
            "explanation": "Recurrent architectures process inputs sequentially while maintaining internal hidden states to capture temporal dependencies."
        },
        {
            "question": "Which algorithm is an example of Unsupervised Machine Learning?",
            "options": {
                "A": "Logistic Regression",
                "B": "K-Means Clustering",
                "C": "Random Forest Classifier",
                "D": "Support Vector Machine"
            },
            "correct_option": "B",
            "explanation": "K-Means partitions unlabelled data into K clusters based on distance metrics without target output labels."
        },
        {
            "question": "What is the main objective of Support Vector Machines (SVM)?",
            "options": {
                "A": "To find a decision boundary/hyperplane that maximizes the margin between classes",
                "B": "To calculate conditional probabilities for all features",
                "C": "To minimize tree depth in ensemble learning",
                "D": "To perform iterative feature selection"
            },
            "correct_option": "A",
            "explanation": "SVM finds an optimal separating hyperplane with maximum margin to nearest support vectors."
        },
        {
            "question": "In the Bias-Variance tradeoff, what symptom characterizes a model with High Bias?",
            "options": {
                "A": "Underfitting (oversimplifying assumptions about the data)",
                "B": "Overfitting (high sensitivity to small fluctuations)",
                "C": "Perfect generalization on test sets",
                "D": "Excessive model parameters"
            },
            "correct_option": "A",
            "explanation": "High bias causes underfitting because the algorithm misses relevant relations between features and target outputs."
        },
        {
            "question": "Which activation function is most effective in preventing the Vanishing Gradient problem in deep networks?",
            "options": {
                "A": "Sigmoid",
                "B": "TanH",
                "C": "ReLU (Rectified Linear Unit)",
                "D": "Softmax"
            },
            "correct_option": "C",
            "explanation": "ReLU maintains a non-saturating derivative of 1 for positive inputs, avoiding gradient vanishing during backpropagation."
        },
        {
            "question": "What is the primary purpose of Principal Component Analysis (PCA)?",
            "options": {
                "A": "Supervised classification of text data",
                "B": "Dimensionality reduction while preserving maximum variance",
                "C": "Hyperparameter optimization",
                "D": "Data augmentation for images"
            },
            "correct_option": "B",
            "explanation": "PCA projects high-dimensional data onto orthogonal axes (principal components) that maximize variance."
        },
        {
            "question": "In a 2x2 Confusion Matrix for binary classification, what do the diagonal elements represent?",
            "options": {
                "A": "True Positives and True Negatives (Correct Predictions)",
                "B": "False Positives and False Negatives (Errors)",
                "C": "Only False Alarm rates",
                "D": "Unclassified instances"
            },
            "correct_option": "A",
            "explanation": "The main diagonal contains True Positives and True Negatives, representing all accurately classified samples."
        }
    ],
    "Web Development": [
        {
            "question": "What is the key advantage of the Virtual DOM used in React?",
            "options": {
                "A": "Directly manipulates browser DOM elements",
                "B": "Minimizes actual DOM re-renders via efficient diffing",
                "C": "Executes CSS styling on a separate thread",
                "D": "Bypasses HTTP header parsing"
            },
            "correct_option": "B",
            "explanation": "React's Virtual DOM calculates minimal DOM updates using a diffing algorithm, greatly improving render performance."
        },
        {
            "question": "Which HTTP status code signifies a resource was successfully created on the server?",
            "options": {
                "A": "200 OK",
                "B": "201 Created",
                "C": "204 No Content",
                "D": "301 Moved Permanently"
            },
            "correct_option": "B",
            "explanation": "HTTP status code 201 indicates that the request succeeded and a new resource was successfully created as a result."
        },
        {
            "question": "What does CORS stand for in web application architecture?",
            "options": {
                "A": "Cross-Origin Resource Sharing",
                "B": "Client-Object Routing Service",
                "C": "Centralized Origin Response Standard",
                "D": "Component-Oriented Render Script"
            },
            "correct_option": "A",
            "explanation": "Cross-Origin Resource Sharing (CORS) is a HTTP-header based mechanism that allows a server to indicate any origins other than its own from which a browser should permit loading resources."
        },
        {
            "question": "In CSS layout, which property removes an element from the normal document flow and positions it relative to its nearest positioned ancestor?",
            "options": {
                "A": "position: relative",
                "B": "position: absolute",
                "C": "position: static",
                "D": "display: flex"
            },
            "correct_option": "B",
            "explanation": "An element with position: absolute is removed from normal flow and positioned relative to its containing ancestor block."
        },
        {
            "question": "What is the primary function of middleware in Express / Node.js frameworks?",
            "options": {
                "A": "Compiling HTML templates into JSX",
                "B": "Executing functions with access to Request, Response, and Next objects",
                "C": "Establishing physical database connections",
                "D": "Minifying client-side JavaScript assets"
            },
            "correct_option": "B",
            "explanation": "Middleware functions have access to the request object (req), response object (res), and the next middleware function in the request-response cycle."
        },
        {
            "question": "What effect does the CSS property 'box-sizing: border-box' have on element sizing?",
            "options": {
                "A": "Includes padding and border within the specified width and height",
                "B": "Adds extra margin equal to border width",
                "C": "Forces element to fill 100% of parent width",
                "D": "Excludes padding from total rendered width"
            },
            "correct_option": "A",
            "explanation": "With border-box, the width and height properties include content, padding, and border."
        },
        {
            "question": "In JavaScript Promises, what state is a Promise in before it has been settled (fulfilled or rejected)?",
            "options": {
                "A": "Resolved",
                "B": "Pending",
                "C": "Fulfilled",
                "D": "Settled"
            },
            "correct_option": "B",
            "explanation": "A Promise starts in the Pending state until it is either fulfilled with a value or rejected with a reason."
        },
        {
            "question": "Which HTTP method is specifically intended for applying partial modifications to a resource?",
            "options": {
                "A": "PUT",
                "B": "PATCH",
                "C": "POST",
                "D": "GET"
            },
            "correct_option": "B",
            "explanation": "PATCH requests update part of an existing resource, whereas PUT replaces the target resource entirely."
        },
        {
            "question": "What is the key difference between localStorage and sessionStorage in web browsers?",
            "options": {
                "A": "localStorage holds up to 50MB while sessionStorage holds 5MB",
                "B": "sessionStorage data persists even after browser restarts",
                "C": "localStorage data has no expiration time; sessionStorage expires when browser tab closes",
                "D": "sessionStorage is automatically transmitted in HTTP request headers"
            },
            "correct_option": "C",
            "explanation": "localStorage data persists until explicitly cleared, while sessionStorage is cleared when the page session ends."
        },
        {
            "question": "What is the main purpose of Web Workers in modern web development?",
            "options": {
                "A": "Running JavaScript scripts in background threads without blocking UI responsiveness",
                "B": "Replacing Service Workers for offline caching",
                "C": "Bypassing browser CORS policy restrictions",
                "D": "Executing server-side Node.js code inside the browser"
            },
            "correct_option": "A",
            "explanation": "Web Workers allow execution of heavy script computations in background threads separate from the main execution thread."
        },
        {
            "question": "Which technique is recommended to defend web applications against SQL Injection attacks?",
            "options": {
                "A": "Client-side form input validation only",
                "B": "Using Parameterized Queries / Prepared Statements",
                "C": "Encoding all database outputs as HTML entities",
                "D": "Encrypting database table names"
            },
            "correct_option": "B",
            "explanation": "Prepared statements ensure user input is treated strictly as data parameters rather than executable SQL code."
        },
        {
            "question": "In CSS Flexbox layout, which property aligns items along the main axis?",
            "options": {
                "A": "align-items",
                "B": "justify-content",
                "C": "align-content",
                "D": "flex-wrap"
            },
            "correct_option": "B",
            "explanation": "justify-content defines flex item alignment along the main axis, while align-items defines alignment along cross axis."
        },
        {
            "question": "Which HTML5 semantic element should encapsulate primary site navigation links?",
            "options": {
                "A": "<header>",
                "B": "<nav>",
                "C": "<section>",
                "D": "<aside>"
            },
            "correct_option": "B",
            "explanation": "The <nav> tag specifies a section of major navigation links in HTML5 document structure."
        },
        {
            "question": "What value is returned by evaluating 'typeof null' in standard JavaScript?",
            "options": {
                "A": "'null'",
                "B": "'undefined'",
                "C": "'object'",
                "D": "'boolean'"
            },
            "correct_option": "C",
            "explanation": "In JavaScript, typeof null returns 'object', which is a historical implementation bug in early JS versions."
        },
        {
            "question": "What is the distinction between HTTP 401 Unauthorized and 403 Forbidden status codes?",
            "options": {
                "A": "401 means authentication is required; 403 means authenticated user lacks necessary permissions",
                "B": "401 means resource not found; 403 means server error",
                "C": "401 applies only to GET requests; 403 applies to POST requests",
                "D": "They are completely identical and interchangeable"
            },
            "correct_option": "A",
            "explanation": "401 indicates lack of valid authentication credentials, while 403 indicates authentication succeeded but access is forbidden."
        }
    ],
    "DEFAULT": [
        {
            "question": "What is the worst-case time complexity of Quick Sort?",
            "options": {
                "A": "O(N log N)",
                "B": "O(N)",
                "C": "O(N^2)",
                "D": "O(log N)"
            },
            "correct_option": "C",
            "explanation": "Quick Sort has a worst-case time complexity of O(N^2) when bad pivot choices (such as smallest/largest element) are repeatedly selected."
        },
        {
            "question": "Which data structure follows the Last-In-First-Out (LIFO) principle?",
            "options": {
                "A": "Queue",
                "B": "Stack",
                "C": "Linked List",
                "D": "Binary Tree"
            },
            "correct_option": "B",
            "explanation": "A Stack operates on LIFO order, where the last element inserted is the first one removed."
        },
        {
            "question": "In SQL, which clause is used to filter records AFTER an aggregation operation?",
            "options": {
                "A": "WHERE",
                "B": "HAVING",
                "C": "GROUP BY",
                "D": "ORDER BY"
            },
            "correct_option": "B",
            "explanation": "The HAVING clause was added to SQL because the WHERE keyword could not be used with aggregate functions."
        },
        {
            "question": "What is the primary benefit of Dependency Injection in object-oriented software design?",
            "options": {
                "A": "Increases execution speed of database queries",
                "B": "Reduces tight coupling between components, enhancing testability",
                "C": "Eliminates memory leaks automatically",
                "D": "Replaces standard constructor functions"
            },
            "correct_option": "B",
            "explanation": "Dependency Injection decouples class implementation details from dependent objects, simplifying unit testing and component swapping."
        },
        {
            "question": "Which OSI layer is responsible for end-to-end packet delivery and IP routing?",
            "options": {
                "A": "Data Link Layer",
                "B": "Network Layer",
                "C": "Transport Layer",
                "D": "Session Layer"
            },
            "correct_option": "B",
            "explanation": "The Network Layer (Layer 3) handles IP addressing, packet routing, and forwarding across networks."
        },
        {
            "question": "What is the average time complexity for searching an element in a balanced Binary Search Tree (BST)?",
            "options": {
                "A": "O(1)",
                "B": "O(log N)",
                "C": "O(N)",
                "D": "O(N log N)"
            },
            "correct_option": "B",
            "explanation": "In a balanced BST, search operations halve the search space at each node, resulting in O(log N) average time complexity."
        },
        {
            "question": "Which of the following is NOT one of Coffman's four necessary conditions for Deadlock?",
            "options": {
                "A": "Mutual Exclusion",
                "B": "Hold and Wait",
                "C": "Preemption Allowed",
                "D": "Circular Wait"
            },
            "correct_option": "C",
            "explanation": "No Preemption is a required deadlock condition. Preemption allowed prevents deadlocks."
        },
        {
            "question": "What is the role of Garbage Collection in managed runtime environments like Java or Python?",
            "options": {
                "A": "Automatic deallocation of unreferenced memory objects",
                "B": "Compiling source code into machine bytecode",
                "C": "Managing thread priorities in CPU scheduler",
                "D": "Optimizing SQL query execution plans"
            },
            "correct_option": "A",
            "explanation": "Garbage collectors identify and reclaim memory occupied by objects no longer reachable by the application."
        },
        {
            "question": "What is the average-case time complexity of insertion and lookup in a Hash Table?",
            "options": {
                "A": "O(1)",
                "B": "O(log N)",
                "C": "O(N)",
                "D": "O(N^2)"
            },
            "correct_option": "A",
            "explanation": "Hash Tables achieve O(1) average constant time complexity by calculating array indices via hash functions."
        },
        {
            "question": "In Object-Oriented Programming, what concept describes overriding a parent method implementation in a child class?",
            "options": {
                "A": "Abstraction",
                "B": "Polymorphism (Dynamic/Runtime)",
                "C": "Encapsulation",
                "D": "Multiple Inheritance"
            },
            "correct_option": "B",
            "explanation": "Method overriding allows sub-classes to provide specific implementations of methods declared in base classes at runtime."
        },
        {
            "question": "What is the core structural distinction between a Process and a Thread in operating systems?",
            "options": {
                "A": "Threads have independent address spaces; processes share address spaces",
                "B": "Processes have independent memory address spaces; threads share parent process memory space",
                "C": "Processes run on GPU; threads run on CPU",
                "D": "Threads cannot perform I/O operations"
            },
            "correct_option": "B",
            "explanation": "Processes are isolated execution environments with dedicated address space; threads within a process share heap and code segments."
        },
        {
            "question": "Which data structure is fundamentally required when performing a Breadth-First Search (BFS) on a Graph?",
            "options": {
                "A": "Stack",
                "B": "Queue",
                "C": "Priority Queue",
                "D": "Binary Heap"
            },
            "correct_option": "B",
            "explanation": "BFS uses a Queue (FIFO) to explore graph nodes level-by-level in order of discovery."
        },
        {
            "question": "In Relational Database systems, what does the 'I' stand for in ACID transaction properties?",
            "options": {
                "A": "Integrity",
                "B": "Isolation",
                "C": "Indexability",
                "D": "Immutability"
            },
            "correct_option": "B",
            "explanation": "Isolation ensures concurrent database transaction executions leave the database in the same state as if executed sequentially."
        },
        {
            "question": "What distinguishes Asymmetric Encryption from Symmetric Encryption?",
            "options": {
                "A": "Symmetric uses a public key; Asymmetric uses no key",
                "B": "Asymmetric uses a key pair (public key for encryption, private key for decryption)",
                "C": "Symmetric encryption is only usable for text files",
                "D": "Asymmetric encryption does not support SSL/TLS certificates"
            },
            "correct_option": "B",
            "explanation": "Asymmetric cryptography relies on mathematically linked public and private key pairs for encryption and decryption."
        },
        {
            "question": "Which statement accurately compares TCP and UDP transport protocols?",
            "options": {
                "A": "TCP is connection-oriented and guarantees packet delivery; UDP is connectionless and lightweight",
                "B": "UDP guarantees packet order; TCP does not",
                "C": "TCP is faster than UDP for live audio streaming",
                "D": "UDP requires 3-way handshake prior to data transmission"
            },
            "correct_option": "A",
            "explanation": "TCP provides reliable, ordered stream delivery via handshakes and acknowledgments, whereas UDP provides low-latency connectionless datagrams."
        }
    ]
}


class MockProvider(BaseAIProvider):
    """
    Mock AI Provider supplying structured question banks when Gemini is disabled or unavailable.
    """

    def generate_questions(self, request: QuestionRequest, prompt: str) -> List[Dict[str, Any]]:
        """
        Retrieves mock technical questions tailored to requested domain or company.
        Guarantees returning request.count (default 15) questions.
        """
        logger.info(f"MockProvider generating questions for target '{request.domain or request.company}'...")

        target_key = request.domain if request.domain in MOCK_QUESTION_BANK else "DEFAULT"
        bank = MOCK_QUESTION_BANK.get(target_key, MOCK_QUESTION_BANK["DEFAULT"])

        requested_count = request.count if request.count else 15

        # Build list of requested count by repeating bank items if bank size < requested_count
        result = []
        while len(result) < requested_count:
            for q in bank:
                if len(result) >= requested_count:
                    break
                result.append(q)

        logger.info(f"MockProvider returning {len(result)} fallback questions.")
        return result
