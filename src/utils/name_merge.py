
import os
from collections import defaultdict
from sentence_transformers import SentenceTransformer, util
from fuzzywuzzy import fuzz
import pandas as pd
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from collections import Counter

def extract_unique_names_and_entities(df):
    # Get unique values from 'Name' column
    unique_names = df['Name'].dropna().unique()
    
    # Get unique values from 'Entity' column
    unique_entities = df['Entity'].dropna().unique()
    
    # Combine both lists and remove duplicates
    unique_combined = list(set(unique_names) | set(unique_entities))
    
    return unique_combined



def group_similar_entities(entity_list):
    # 1. Convert List to DataFrame
    df = pd.DataFrame({'Entity': entity_list})
    df['Cleaned_Entity'] = df['Entity']

    # 2. Generate Name Embeddings
    model = SentenceTransformer(os.path.dirname(os.path.abspath(__file__))+"/matching_names_model")
    unique_entities = df['Cleaned_Entity'].unique()
    embeddings = model.encode(unique_entities)
    embedding_df = pd.DataFrame({'Cleaned_Entity': unique_entities, 'Embedding': list(embeddings)})

    # 3. Clustering Similar Names
    embedding_matrix = np.vstack(embedding_df['Embedding'].values)
    clustering_model = AgglomerativeClustering(
        n_clusters=None,
        metric='cosine',
        distance_threshold=0.33,
        linkage='average'
    )
    labels = clustering_model.fit_predict(embedding_matrix)
    embedding_df['Cluster'] = labels

    # 4. Map Clusters Back to Original List
    result_df = pd.DataFrame({'Entity': entity_list})
    result_df = result_df.merge(embedding_df[['Cleaned_Entity', 'Cluster']], 
                                left_on='Entity', 
                                right_on='Cleaned_Entity', 
                                how='left')

    # 5. Review Clusters
    cluster_groups = result_df.groupby('Cluster')['Entity'].unique().reset_index()
    cluster_groups = cluster_groups[cluster_groups['Entity'].apply(len) > 1].reset_index(drop=True)

    all_entities_list = []
    # Function to compute the majority starting letter of entities in a cluster
    def majority_letter(entities):
        # Extract first letters of valid entities
        first_letters = [str(entity).strip()[0].lower() for entity in entities if isinstance(entity, str) and entity.strip()]
        if not first_letters:
            return ''  # Default if no valid entities
        # Find the most common starting letter
        return Counter(first_letters).most_common(1)[0][0]

    # Add majority letter to each cluster
    cluster_groups['Majority_Letter'] = cluster_groups['Entity'].apply(majority_letter)

    # Sort clusters by the majority starting letter
    cluster_groups = cluster_groups.sort_values(by='Majority_Letter').reset_index(drop=True)

    # Display clusters
    for idx, row in cluster_groups.iterrows():
        cluster_id = row['Cluster']
        entities_in_cluster = sorted([str(entity) for entity in row['Entity'] if isinstance(entity, str)], key=lambda x: x.lower())
        all_entities_list.append(entities_in_cluster)

    return all_entities_list


def replace_entities(process_df, lists_of_names):
    """
    Efficiently replaces values in the 'Entity' column based on a list of lists of names.
    """
    # Create a set of unique names in the 'Name' column for fast lookup
    name_set = set(process_df['Name'].dropna())

    # Precompute the most frequent value for each group in 'Entity'
    entity_counts = process_df['Entity'].value_counts()

    # Iterate over each group in the list of lists
    replacements = {}
    for name_group in lists_of_names:
        # Check if any name in the group exists in the 'Name' column
        anchor_name = next((name for name in name_group if name in name_set), None)

        if anchor_name:
            # Use the anchor name for replacements
            replacements.update({name: anchor_name for name in name_group})
        else:
            # Find the most frequent name in 'Entity' from the group
            most_frequent_name = (
                entity_counts[entity_counts.index.isin(name_group)].idxmax()
                if not entity_counts[entity_counts.index.isin(name_group)].empty
                else name_group[0]  # Default to the first name
            )
            replacements.update({name: most_frequent_name for name in name_group})

    # Apply the replacements to the 'Entity' column
    process_df['Entity'] = process_df['Entity'].replace(replacements)

    return process_df
