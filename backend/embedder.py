import os
import logging
from typing import List

logger = logging.getLogger(__name__)

# Monkey patch to handle 404 errors for optional files
def patch_huggingface_hub():
    """Patch transformers.utils.hub to ignore 404 errors for additional_chat_templates."""
    try:
        # Patch transformers.utils.hub.list_repo_templates - this is where the error occurs
        import transformers.utils.hub as hub_module
        
        # Check if list_repo_templates exists
        if hasattr(hub_module, 'list_repo_templates'):
            original_list_repo_templates = hub_module.list_repo_templates
            
            def patched_list_repo_templates(*args, **kwargs):
                try:
                    return original_list_repo_templates(*args, **kwargs)
                except Exception as e:
                    error_str = str(e).lower()
                    if "additional_chat_templates" in error_str or ("404" in error_str and "not found" in error_str):
                        # This is an optional file, return empty list
                        logger.debug(f"Ignoring 404 for additional_chat_templates")
                        return []
                    raise
            
            hub_module.list_repo_templates = patched_list_repo_templates
        
        # Also patch huggingface_hub's list_repo_tree if it exists
        try:
            from huggingface_hub import hf_api
            if hasattr(hf_api, 'HfApi') and hasattr(hf_api.HfApi, 'list_repo_tree'):
                original_list_repo_tree = hf_api.HfApi.list_repo_tree
                
                def patched_list_repo_tree(self, *args, **kwargs):
                    try:
                        return original_list_repo_tree(self, *args, **kwargs)
                    except Exception as e:
                        error_str = str(e).lower()
                        if "additional_chat_templates" in error_str or ("404" in error_str and "not found" in error_str):
                            logger.debug(f"Ignoring 404 for additional_chat_templates in list_repo_tree")
                            return []
                        raise
                
                hf_api.HfApi.list_repo_tree = patched_list_repo_tree
        except Exception:
            pass
            
    except Exception as e:
        logger.debug(f"Could not patch libraries: {e}")
        pass  # If patching fails, continue anyway

DEFAULT_MODELS = [
    "all-MiniLM-L6-v2",  # Simple, reliable model
    "sentence-transformers/all-MiniLM-L6-v2",  # Fallback with full path
    "law-ai/InLegalBERT",  # Preferred for Indian legal cases
    "nlpaueb/legal-bert-base-uncased",
]


class SentenceEmbedder:
    def __init__(self, model_name: str | None = None, device: str | None = None, batch_size: int | None = None):
        # Patch huggingface_hub before importing
        patch_huggingface_hub()
        
        import torch
        from sentence_transformers import SentenceTransformer
        
        self.model_name = model_name or os.getenv("MODEL_NAME") or DEFAULT_MODELS[0]
        self.device = device or os.getenv("DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")
        self.batch_size = int(batch_size or os.getenv("BATCH_SIZE") or (64 if self.device == "cuda" else 16))
        
        # Try models in fallback order
        models_to_try = [self.model_name] + [m for m in DEFAULT_MODELS if m != self.model_name]
        
        self.model = None
        import warnings
        
        for model_candidate in models_to_try:
            try:
                logger.info(f"Attempting to load model: {model_candidate}")
                
                # Suppress all warnings during model loading
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    try:
                        self.model = SentenceTransformer(model_candidate, device=self.device)
                    except Exception as load_error:
                        error_str = str(load_error).lower()
                        # If it's just a 404 for optional files (additional_chat_templates), 
                        # try to load the model from cache anyway - the core files are there
                        if "additional_chat_templates" in error_str or ("404" in error_str and "not found" in error_str):
                            logger.info(f"Got 404 for optional file, but model core files exist. Attempting to load from cache...")
                            try:
                                # Try loading directly from the cached model files
                                # The model.safetensors file should be in the cache
                                cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
                                
                                # Try with a fresh SentenceTransformer instance
                                # Sometimes the model loads despite the 404
                                import sys
                                import io
                                
                                # Suppress stderr temporarily
                                old_stderr = sys.stderr
                                sys.stderr = io.StringIO()
                                try:
                                    self.model = SentenceTransformer(model_candidate, device=self.device)
                                finally:
                                    sys.stderr.close()
                                    sys.stderr = old_stderr
                                
                                # If we got here, model loaded despite the error
                                if self.model is not None:
                                    logger.info(f"Successfully loaded {model_candidate} despite 404 warning")
                                else:
                                    raise load_error
                            except Exception as e2:
                                logger.warning(f"Could not load {model_candidate} from cache: {e2}")
                                raise load_error
                        else:
                            raise load_error
                
                # Verify model actually loaded and works
                if self.model is not None:
                    # Test encode to make sure it works
                    try:
                        test_embedding = self.model.encode(["test"], convert_to_numpy=True, show_progress_bar=False)
                        if test_embedding is not None and len(test_embedding) > 0:
                            self.model_name = model_candidate
                            logger.info(f"Successfully loaded model: {model_candidate} on {self.device}")
                            break
                        else:
                            self.model = None
                            logger.warning(f"Model {model_candidate} loaded but encode test failed")
                    except Exception as test_error:
                        self.model = None
                        logger.warning(f"Model {model_candidate} encode test failed: {test_error}")
                        
            except Exception as e:
                logger.warning(f"Failed to load {model_candidate}: {e}")
                continue
        
        if self.model is None:
            raise RuntimeError(f"Could not load any of the models: {models_to_try}")

    def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts to embeddings."""
        import numpy as np
        
        if not texts:
            return []
        
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 100,
        )
        
        # Convert to float32 and list format
        return embeddings.astype('float32').tolist()
