import gc
import sys
# For Day 2, we will use a lightweight scikit-learn pipeline or a tiny HuggingFace model.
# Let's write the memory management framework first.

class ModelLifecycleManager:
    def __init__(self):
        self.current_model = None
        self.current_model_name = None

    def free_memory(self):
        """Forcefully evicts the active model from RAM and calls the Garbage Collector."""
        if self.current_model is not None:
            del self.current_model
            self.current_model = None
            self.current_model_name = None
            
        # Clear out internal framework caches if any are imported later
        if "torch" in sys.modules:
            import torch
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            
        gc.collect()

    def load_classifier(self):
        """Lazy loads a fast, low-footprint classification pipeline."""
        if self.current_model_name == "classifier":
            return self.current_model
            
        self.free_memory()
        
        # Using a highly optimized, tiny vectorizer + linear classifier to fit strict RAM envelopes
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        import joblib
        import os

        model_path = "app/resources/classifier_model.pkl"
        
        if os.path.exists(model_path):
            self.current_model = joblib.load(model_path)
        else:
            # Fallback mockup: A simple pipeline trained on minimal text samples
            # In production, pre-train this on your 20-document test set
            texts = [
                "Master services agreement payment terms liability NDA confidentiality",
                "Invoice billing total amount tax due vendor line items",
                "Balance sheet financial statement revenue assets liability net income",
                "Request for proposal RFP requirements scope timeline bid supplier"
            ]
            labels = ["contract", "invoice", "financial_statement", "rfp"]
            
            mock_pipeline = Pipeline([
                ('tfidf', TfidfVectorizer()),
                ('clf', LogisticRegression())
            ])
            mock_pipeline.fit(texts, labels)
            
            os.makedirs("app/resources", exist_ok=True)
            joblib.dump(mock_pipeline, model_path)
            self.current_model = mock_pipeline
            
        self.current_model_name = "classifier"
        return self.current_model

model_registry = ModelLifecycleManager()