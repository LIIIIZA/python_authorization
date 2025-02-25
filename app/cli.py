import click
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from jose import jwt

from .db.session import SessionLocal
from .core.config import settings
from .core.security import get_password_hash
from .crud.user import UserCRUD
from .tasks.worker import NotificationWorker
from db.models.user import UserRole

@click.group()
def cli():
    pass

@cli.command()
@click.option("--email", prompt="Admin email", help="Email администратора")
@click.option("--password", prompt=True, 
              hide_input=True, 
              confirmation_prompt=True,
              help="Пароль администратора")
def create_admin(email: str, password: str):
    db = SessionLocal()
    try:
        user_crud = UserCRUD(db)
        
        if user_crud.get_by_email(email):
            click.echo("❌ Ошибка: пользователь с таким email уже существует")
            return
            
        hashed_password = get_password_hash(password)
        user = user_crud.create(
            email=email,
            hashed_password=hashed_password,
            role=UserRole.ADMIN
        )
        
        db.commit()
        click.echo(f"✅ Администратор {email} успешно создан")
        click.echo(f"ID пользователя: {user.id}")
        
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Ошибка при создании администратора: {str(e)}")
    finally:
        db.close()

@cli.command()
def init_db():
    from app.db.base import Base
    from app.db.session import engine
    
    try:
        Base.metadata.create_all(bind=engine)
        click.echo("✅ Таблицы успешно созданы")
    except Exception as e:
        click.echo(f"❌ Ошибка создания таблиц: {str(e)}")

@cli.command()
def run_worker():
    try:
        worker = NotificationWorker()
        click.echo("🚀 Воркер запущен. Ожидание задач...")
        worker.run()
    except KeyboardInterrupt:
        click.echo("\n🛑 Воркер остановлен")
    except Exception as e:
        click.echo(f"❌ Ошибка воркера: {str(e)}")

@cli.command()
@click.option("--user-id", required=True, help="ID пользователя")
@click.option("--role", default="user", help="Роль пользователя (user/admin)")
@click.option("--expire", default=60, help="Время жизни токена в минутах")
def generate_token(user_id: str, role: str, expire: int):
    try:
        payload = {
            "sub": user_id,
            "role": role,
            "exp": datetime.now() + timedelta(minutes=expire)
        }
        token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        click.echo(f"🔑 Сгенерированный токен:\n{token}")
    except Exception as e:
        click.echo(f"❌ Ошибка генерации токена: {str(e)}")

@cli.command()
def check_services():
    from app.db.session import check_db_connection
    from app.core.redis import ping_redis
    
    click.echo("🔄 Проверка состояния сервисов...")
    
    if check_db_connection():
        click.echo("✅ PostgreSQL: доступен")
    else:
        click.echo("❌ PostgreSQL: недоступен")
    
    if ping_redis():
        click.echo("✅ Redis: доступен")
    else:
        click.echo("❌ Redis: недоступен")

if __name__ == "__main__":
    cli()