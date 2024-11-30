import os
from gliner import GLiNER

# Assuming 'gliner_medium-v2.1' is in the parent directory
current_dir = os.getcwd()
# model_path = os.path.join(current_dir, 'src', 'gliner_medium-v2.1')
model_path = os.path.join(current_dir, 'src', 'sanchay')

# Normalize the path
model_path = os.path.abspath(model_path)

# Load the model
model = GLiNER.from_pretrained(model_path, local_files_only=False)