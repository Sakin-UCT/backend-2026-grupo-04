from collections.abc import Generator
 
from sqlalchemy.orm import Session
 
from app.infrastructure.database import SessionLocal
 
 
def get_db() -> Generator[Session, None, None]:
    """Abre una sesión de BD por solicitud y la cierra siempre al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
