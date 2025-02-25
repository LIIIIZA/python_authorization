from app.db.base import Base
from app.db.session import engine

def init_db():
    from .models.user import User
    from .models.login_history import LoginHistory
    
    Base.metadata.create_all(bind=engine)
