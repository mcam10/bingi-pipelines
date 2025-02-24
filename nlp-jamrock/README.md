# Jamaican Creole-English Translation Similarity

This project focuses on analyzing and improving semantic similarity between Jamaican Creole (Patois) and English translations using modern NLP techniques.

## Overview

The project processes parallel translations between Jamaican Creole and English, utilizing sentence transformers to measure and improve semantic similarity between language pairs.

## Dataset Hosted:
https://huggingface.co/datasets/gearV9/patois_proverbs

## Features

- Parallel text processing for Jamaican Creole and English
- Sentence similarity scoring using transformer models
- Custom model fine-tuning capabilities
- Support for various data formats (CSV, Parquet)

## Installation

```bash
pip install -r requirements.txt

Required packages:

pandas
sentence-transformers
torch
scikit-learn
pyarrow (for parquet files)

Model Performance
Initial similarity scores with base model:

Average similarity score: X
Score range: 0.17-0.76
Areas for improvement identified in short phrases and cultural expressions

Future Improvements

Data augmentation for better coverage
Fine-tuning with contrastive learning
Integration of cultural context
Support for code-switching detection

##Example

```
Jamaican   English  similarity_score
1    Patwa    Patois          0.763368
2    no av  not have          0.583210
3    du it     do it          0.610830
4   gi iin   give in          0.381267
5        a    father          0.338483
6     aliv     olive          0.604036
7      ban      band          0.174508
8      wan       one          0.503427
9     dala    dollar          0.360349
```

##ToDOs
I recommend trying these approaches in this order:

First, try different base models to see if any give better out-of-the-box performance
Then try fine-tuning with contrastive learning
If needed, augment the dataset and fine-tune again

Would you like me to help you implement any of these specific approaches? Also, some of these low scores might be due to:

Short text length (like "a" → "father")
Ambiguous translations
Cultural context that standard models might miss
