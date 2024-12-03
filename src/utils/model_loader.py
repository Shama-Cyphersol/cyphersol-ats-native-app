import os
import sys
from gliner import GLiNER
from appdirs import user_cache_dir
from threading import Lock


class ModelLoader:
    """
    Singleton class to manage the lazy loading of the GLiNER model.
    Ensures that only one instance of the model is created and reused.
    """
    _instance = None
    _lock = Lock()

    APP_NAME = "CypherSOL-App"
    COMPANY_NAME = "CypherSOL"
    cache_dir = user_cache_dir(APP_NAME, COMPANY_NAME)
    model_cache_path = os.path.join(cache_dir, 'gliner_medium-v2.1')

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ModelLoader, cls).__new__(cls)
                    cls._instance._initialize_model()
        return cls._instance
    
    def _initialize_model(self):
        """
        Initializes the model when the class is instantiated.
        Downloads the model if not already cached.
        """
        # if not os.path.exists(self.model_cache_path):
            # print(f"Model not found localcly. Downloading and saving to: {self.model_cache_path}")
        self._model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
            # print("Model downloaded and saved successfully!")
        # else:
            # print(f"Model already cached at: {self.model_cache_path}")
            # self._model = GLiNER.from_pretrained(self.model_cache_path)


    def get_model(self):
        """
        Returns the already initialized model instance.
        """
        return self._model
    

# Instantiate the singleton in the same file
model_loader = ModelLoader()
# model_loader = None
print("Model loaded successfully!")