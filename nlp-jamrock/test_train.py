import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses
from sklearn.metrics.pairwise import cosine_similarity
from torch.utils.data import DataLoader
import torch

# Read the parquet file
df = pd.read_parquet('patois_proverbs/data/train-00000-of-00001.parquet')

# Display basic information
print("Dataset Info:")
print(df.info())

print("\nFirst few rows:")
print(df.iloc[1:100])


model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

# Get embeddings
patois_embeddings = model.encode(df['Jamaican'].tolist())
english_embeddings = model.encode(df['English'].tolist())

# Calculate similarities
similarities = cosine_similarity(patois_embeddings, english_embeddings)

# Add similarity scores
df['similarity_score'] = [similarities[i][i] for i in range(len(df))]

def train_custom_similarity_model(df):
    # Create training examples

    device = torch.device('mps')

    train_examples = [
        InputExample(texts=[row['Jamaican'], row['English']], label=1.0)
        for _, row in df.iterrows()
    ]
    
    # Initialize model
    model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
    
    # Create train dataloader
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=4)
    
    # Use cosine similarity loss
    train_loss = losses.CosineSimilarityLoss(model)
    
    # Train the model
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=10,
        warmup_steps=100,
        show_progress_bar=True
    )
    return model

import os
os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'

## Train the model
model_training = train_custom_similarity_model(df)

