from app import create_app
from extensions import assets

assets._named_bundles = {}
application = create_app()
