import chromadb


def chromadb_operations():

    # =========================================================
    # 1. CREATE CHROMADB CLIENT
    # =========================================================

    client = chromadb.Client()


    # =========================================================
    # 2. CREATE COLLECTION
    # =========================================================

    collection = client.create_collection(
        name="student_collection"
    )


    # =========================================================
    # 3. CREATE VALUES
    # =========================================================

    # IDs
    student_ids = [
        "student1",
        "student2",
        "student3",
        "student4",
        "student5",
        "student6",
        "student7",
        "student8"
    ]


    # Documents
    student_documents = [
        "Alice is an AI and Machine Learning student.",
        "Bob is a Data Science student.",
        "Charlie is a Computer Science student.",
        "David is an AI and Machine Learning student.",
        "Emma is a Cyber Security student.",
        "Frank is a Data Science student.",
        "Grace is an AI and Machine Learning student.",
        "Harry is a Computer Science student."
    ]


    # Embeddings
    student_embeddings = [
        [0.10, 0.20, 0.30],
        [0.20, 0.30, 0.40],
        [0.30, 0.40, 0.50],
        [0.40, 0.50, 0.60],
        [0.50, 0.60, 0.70],
        [0.60, 0.70, 0.80],
        [0.70, 0.80, 0.90],
        [0.80, 0.90, 1.00]
    ]


    # Metadata
    student_metadata = [

        {
            "name": "Alice",
            "branch": "AIML",
            "year": 3,
            "city": "Bangalore",
            "skill": "Python"
        },

        {
            "name": "Bob",
            "branch": "DS",
            "year": 2,
            "city": "Mysore",
            "skill": "Python"
        },

        {
            "name": "Charlie",
            "branch": "CSE",
            "year": 4,
            "city": "Tumkur",
            "skill": "Java"
        },

        {
            "name": "David",
            "branch": "AIML",
            "year": 3,
            "city": "Tumkur",
            "skill": "Python"
        },

        {
            "name": "Emma",
            "branch": "CS",
            "year": 4,
            "city": "Bangalore",
            "skill": "Cyber Security"
        },

        {
            "name": "Frank",
            "branch": "DS",
            "year": 3,
            "city": "Mysore",
            "skill": "SQL"
        },

        {
            "name": "Grace",
            "branch": "AIML",
            "year": 4,
            "city": "Bangalore",
            "skill": "Machine Learning"
        },

        {
            "name": "Harry",
            "branch": "CSE",
            "year": 3,
            "city": "Tumkur",
            "skill": "Java"
        }
    ]


    # =========================================================
    # 4. DISPLAY CREATED VALUES
    # =========================================================

    print("\n========== CREATED VALUES ==========")

    print("\nIDs:")
    print(student_ids)

    print("\nDocuments:")
    for document in student_documents:
        print(document)

    print("\nEmbeddings:")
    for embedding in student_embeddings:
        print(embedding)

    print("\nMetadata:")
    for metadata in student_metadata:
        print(metadata)


    # =========================================================
    # 5. ADD VALUES TO CHROMADB
    # =========================================================

    collection.add(
        ids=student_ids,
        documents=student_documents,
        embeddings=student_embeddings,
        metadatas=student_metadata
    )


    print("\nData successfully added to ChromaDB.")


    # =========================================================
    # 6. BASIC QUERY
    # =========================================================

    print("\n========== BASIC QUERY ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        n_results=3
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 7. ONLY DOCUMENTS
    # =========================================================

    print("\n========== ONLY DOCUMENTS ==========")

    print(results["documents"][0])


    # =========================================================
    # 8. METADATA
    # =========================================================

    print("\n========== METADATA ==========")

    for metadata in results["metadatas"][0]:
        print(metadata)


    # =========================================================
    # 9. EQUAL (=)
    # =========================================================

    print("\n========== BRANCH = AIML ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        where={
            "branch": "AIML"
        },
        n_results=5
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 10. NOT EQUAL ($ne)
    # =========================================================

    print("\n========== BRANCH != AIML ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        where={
            "branch": {
                "$ne": "AIML"
            }
        },
        n_results=5
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 11. IN ($in)
    # =========================================================

    print("\n========== BRANCH IN AIML, DS ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        where={
            "branch": {
                "$in": ["AIML", "DS"]
            }
        },
        n_results=5
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 12. NOT IN ($nin)
    # =========================================================

    print("\n========== BRANCH NOT IN AIML, DS ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        where={
            "branch": {
                "$nin": ["AIML", "DS"]
            }
        },
        n_results=5
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 13. AND
    # =========================================================

    print("\n========== AIML AND 3RD YEAR ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        where={
            "$and": [
                {
                    "branch": "AIML"
                },
                {
                    "year": 3
                }
            ]
        },
        n_results=5
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 14. OR
    # =========================================================

    print("\n========== AIML OR CSE ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        where={
            "$or": [
                {
                    "branch": "AIML"
                },
                {
                    "branch": "CSE"
                }
            ]
        },
        n_results=5
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 15. AND + OR
    # =========================================================

    print("\n========== (AIML OR CSE) AND YEAR 3 ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        where={
            "$and": [

                {
                    "$or": [
                        {
                            "branch": "AIML"
                        },
                        {
                            "branch": "CSE"
                        }
                    ]
                },

                {
                    "year": 3
                }
            ]
        },
        n_results=5
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 16. CITY FILTER
    # =========================================================

    print("\n========== CITY = BANGALORE ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        where={
            "city": "Bangalore"
        },
        n_results=5
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 17. CITY IN
    # =========================================================

    print("\n========== CITY IN BANGALORE, TUMKUR ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        where={
            "city": {
                "$in": ["Bangalore", "Tumkur"]
            }
        },
        n_results=5
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 18. CITY NOT IN
    # =========================================================

    print("\n========== CITY NOT IN MYSORE ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        where={
            "city": {
                "$nin": ["Mysore"]
            }
        },
        n_results=5
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 19. GREATER THAN ($gt)
    # =========================================================

    print("\n========== YEAR > 3 ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        where={
            "year": {
                "$gt": 3
            }
        },
        n_results=5
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 20. GREATER THAN OR EQUAL ($gte)
    # =========================================================

    print("\n========== YEAR >= 3 ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        where={
            "year": {
                "$gte": 3
            }
        },
        n_results=5
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 21. LESS THAN OR EQUAL ($lte)
    # =========================================================

    print("\n========== YEAR <= 3 ==========")

    results = collection.query(
        query_embeddings=[[0.20, 0.30, 0.40]],
        where={
            "year": {
                "$lte": 3
            }
        },
        n_results=5
    )

    for document in results["documents"][0]:
        print(document)


    # =========================================================
    # 22. GET BY ID
    # =========================================================

    print("\n========== GET BY ID ==========")

    result = collection.get(
        ids=["student1"]
    )

    print(result)


    # =========================================================
    # 23. GET USING WHERE
    # =========================================================

    print("\n========== GET AIML STUDENTS ==========")

    result = collection.get(
        where={
            "branch": "AIML"
        }
    )

    for document in result["documents"]:
        print(document)


    # =========================================================
    # 24. GET ONLY IDs
    # =========================================================

    print("\n========== ALL IDs ==========")

    result = collection.get()

    print(result["ids"])


    # =========================================================
    # 25. COLLECTION COUNT
    # =========================================================

    print("\n========== COLLECTION COUNT ==========")

    print(
        "Total documents:",
        collection.count()
    )


# =============================================================
# RUN FUNCTION
# =============================================================

chromadb_operations()