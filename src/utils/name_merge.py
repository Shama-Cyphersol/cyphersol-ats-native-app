
import os
from collections import defaultdict
from sentence_transformers import SentenceTransformer, util
from fuzzywuzzy import fuzz




def extract_unique_names_and_entities(df):
    # Get unique values from 'Name' column
    unique_names = df['Name'].dropna().unique()
    
    # Get unique values from 'Entity' column
    unique_entities = df['Entity'].dropna().unique()
    
    # Combine both lists and remove duplicates
    unique_combined = list(set(unique_names) | set(unique_entities))
    
    return unique_combined



def group_similar_entities(entities, low=0.62, high=1.0, weight_semantic=0.6, weight_string=0.4):
    structure_model = SentenceTransformer(os.path.dirname(os.path.abspath(__file__))+"./matching_names_model")

    n = len(entities)
    grouped = defaultdict(list)
    visited = set()

    # Precompute embeddings for semantic similarity
    embeddings = structure_model.encode(entities, convert_to_tensor=True)

    for i in range(n):
        for j in range(i + 1, n):
            # Calculate semantic similarity
            semantic_score = util.cos_sim(embeddings[i], embeddings[j]).item()

            # Calculate string similarity
            string_score = fuzz.ratio(entities[i].lower(), entities[j].lower()) / 100

            # Combine the scores
            combined_score = (weight_semantic * semantic_score) + (weight_string * string_score)

            if low <= combined_score < high and (entities[i], entities[j]) not in visited:
                grouped[entities[i]].append(entities[j])
                visited.add((entities[i], entities[j]))
                visited.add((entities[j], entities[i]))

    # Consolidate groups into lists
    result = []
    for key, value in grouped.items():
        result.append([key] + value)

    # Merge overlapping groups
    merged = []
    while result:
        first, *rest = result
        first = set(first)
        overlapping = [g for g in rest if first & set(g)]
        for g in overlapping:
            first |= set(g)
        rest = [g for g in rest if not (first & set(g))]
        merged.append(list(first))
        result = rest

    return merged


def replace_entities(self, df, lists_of_names):
    """
    Efficiently replaces values in the 'Entity' column based on a list of lists of names.
    """
    # Create a set of unique names in the 'Name' column for fast lookup
    name_set = set(df['Name'].dropna())

    # Precompute the most frequent value for each group in 'Entity'
    entity_counts = df['Entity'].value_counts()

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
    df['Entity'] = df['Entity'].replace(replacements)

    return df
