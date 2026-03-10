# My Data Portfolio

Welcome to my data portfolio! This repository showcases my data skills using real-world datasets.

---

## Projects

### 1. Olist Project – E-commerce Data Analysis
**Description:**  
Analyzed Brazilian e-commerce data from Olist to study order delays and regional trends. Built a complete workflow from data ingestion to visualization.

**Repository:** [Olist Project](./olist_project)

### 2. Spatial Project – Using Cellular Automata Model to simulate housing density
**Description:** 
This research develops a Cellular Automata (CA) model to simulate and forecast housing density changes in Leidsche Rijn, Utrecht, under Transit-Oriented Development (TOD) policies. The model is trained on 2010&2015 land-use data, validated with 2017 data, and used to project development up to 2040. Two scenarios—baseline and TOD—are compared to assess spatial impacts of the proposed policy. The study includes full workflow: data preprocessing, logistic regression-based transition modeling, CA simulation, policy integration, and visualization of results.

**Repository:** [Spatial_Project_Cellular_Automata](./Spatial_Project_Cellular_Automata)

### 3. E-commerce Precision Marketing & Growth Strategy: The RFM-I Optimization Framework
**Description:** 
This project addresses the "Inefficient Subsidy" challenge in e-commerce marketing by developing an enhanced RFM-I (Recency, Frequency, Monetary, Intent) user segmentation model.

While traditional RFM models focus on historical value, this framework introduces Real-time Intent (I)—calculated from session duration and page depth—to identify "High-Intent Hesitators." These are users who are most sensitive to marketing nudges but are typically overlooked by backward-looking models.

**Repository:** [Ecommerce_rfmproject](./Ecommerce_rfmproject)


## Courseworks

### 1. Infomwr Assignment 1 - database design and querying
**Description:**
This assignment focuses on **relational database design, SQL querying, and Python-based data extraction**.  
We redesigned a company database by expanding the schema with new entities such as **Bill**, **Product**, and **Employee**, and defined both **one-to-many** and **many-to-many** relationships.  
Normalization was performed to ensure that the database schema satisfies **BCNF**.  

In the querying part, we implemented multiple **SQL queries** involving joins, aggregation, and nested subqueries.  
Finally, we used **Python (SQLite + Pandas)** to connect to the database, load tables into DataFrames, and applied a **Jaccard similarity function** to identify similar customer records.

**Respository:** [Infomwr Assignment 1](./Infomwr%20Assignment%201)

### 2. Infomwr Assignment 2: Data Integration & Preparation
**Description:**
This project is part of the INFOMDWR course Assignment 2, focusing on **data integration and preparation**. It involves profiling, cleaning, and integrating data from a road safety dataset using Python. The work includes generating summary statistics to understand data characteristics, handling missing and inconsistent values, and merging multiple data sources to produce a coherent, high-quality dataset ready for analysis.

**Respository:** [Infomwr Assignment 2](./Infomwr%20Assignment%202)

### 3. Infomwr Assignment 3 - supervised learning competition
**Description:**
This assignment follows the **Common Task Framework (CTF)**.  
We were provided with a dataset containing student information, and our goal was to **predict academic performance**.  

In this project, we implemented and compared several supervised learning models — **Linear Regression**, **K-Nearest Neighbors (KNN)**, and **Random Forest** — to predict students' outcomes.  
Finally, we submitted our predictions to the designated “referee” system for evaluation.

**Respository:** [Infomwr Assignment 3](./Infomwr%20Assignment%203)

### 4. Infomwr Assignment 4 - Text Clustering
**Description:**
A comprehensive text clustering project analyzing 5000 IMDb movie reviews. We apply K-means, GMM, agglomerative clustering, and LDA to identify sentiment patterns and thematic structures. The report evaluates model performance using TF-IDF and SBERT embeddings, with comparisons based on silhouette scores, cluster stability, and perplexity to determine the most coherent and stable clustering approach for uncovering meaningful textual groupings.

**Respository:** [Infomwr Assignment 4](./Infomwr%20Assignment%204)

### 5. INFOMTALC Midterm Assignment - Transformer Chess Player
**Description:**
This project implements a transformer-based chess player for a tournament framework, where the agent generates moves from FEN positions using a pre-trained language model SmolLM2 fine-tuned specifically on chess games. The model, [shawnno/chess-smollm2](https://huggingface.co/Shawnno/chess-smollm2), was trained on datasets from Lichess and Stockfish engine generated games which contains more than 150k records formatted as FEN-to-move pairs with special tokens <|fen|> and <|move|> .

**Respository:** [INFOMTALC_Assignment1_chessbot](./INFOMTALC_Assignment1_chessbot)

### 6. INFOMTMA Final Group Project - Comparative NLP Analysis of Political Discourse on YouTube (Trump vs. Biden)
**Description:**
A comprehensive Data Science research project analyzing the linguistic patterns of sarcasm in overpolarized political discussions on YouTube. By implementing a deep learning pipeline centered on the roBERTa model, I quantified how sarcasm is utilized as a rhetorical tool across different political camps. The project integrates K-Means clustering for topic modeling and sentiment polarity detection to reveal how social media audiences express criticism and group affiliation through irony and satire.

**Respository:** [biden_trump_sarcasm_project](./biden_trump_sarcasm_project)

## Future Plans
- Add more data analysis/data pipeline projects
- Expand portfolio with end-to-end analytics workflows

## License

MIT License












