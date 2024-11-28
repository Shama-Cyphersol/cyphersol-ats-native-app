import os
from gliner import GLiNER

# Assuming 'gliner_medium-v2.1' is in the 'src' directory
current_dir = os.getcwd()
model_path = os.path.join(current_dir, 'src', 'gliner_medium-v2.1')

# Normalize the path
model_path = os.path.abspath(model_path)

# Load the model from a local path
try:
    model = GLiNER.from_pretrained("urchade/gliner_medium-v2")
except Exception as e:
    print(f"Error loading model: {e}")