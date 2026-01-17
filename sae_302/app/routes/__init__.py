from app.routes.auth import auth_bp
from app.routes.users import user_bp
from app.routes.serveurs import serveurs_bp
from app.routes.journaux import journaux_bp

# import des differentes routes
blueprints = ['auth_bp', 'user_bp', 'serveurs_bp', 'journaux_bp']