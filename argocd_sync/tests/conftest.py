import os
import sys

# Expose argocd_sync/ modules (fetch, transform, upsert, versions) to tests.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
