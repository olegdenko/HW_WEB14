import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

sys.path.append(str(Path(__file__).parent.parent))
Base = declarative_base()


from src.repository.users import get_user_by_email, create_user, update_avatar, update_token, confirmed_email
from src.database import models
from src.database.models import User
from src.schemas import UserModel
from src.database.models import Role

# Define an SQLite database URL in memory for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create an engine and SessionLocal for the SQLite database in memory
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db() -> Session:
    db = TestingSessionLocal()
    try:
        models.Base.metadata.create_all(bind=engine, tables=[User.__table__])
        yield db
    finally:
        db.close()

@pytest.mark.asyncio
async def test_get_user_by_email(db: Session):
    # Test case when the user is not present in the database
    result = await get_user_by_email("nonexistent@example.com", db)
    assert result is None

    # Create a user in the database
    user_data = UserModel(username="testuser", email="test@example.com", password="password", roles=Role.admin)
    created_user = await create_user(user_data, db)

    # Test case when the user is present in the database
    result = await get_user_by_email("test@example.com", db)
    assert result is not None
    assert result.email == "test@example.com"
    assert result.id == created_user.id

# @pytest.mark.asyncio
# async def test_create_user(db: Session):
#     # Test case for creating a user
#     user_data = UserModel(username="testuser", email="test@example.com", password="password", roles=['user'])
#     created_user = await create_user(user_data, db)
#     assert created_user is not None
#     assert created_user.email == "test@example.com"
#     assert created_user.avatar is not None
#     assert created_user.roles == Role.user.value

#     # Test case for creating a user with the same email (should raise an exception)
#     with pytest.raises(Exception):
#         await create_user(user_data, db)


@pytest.mark.asyncio
async def test_create_user(db: Session):
    # Тестовий випадок для створення користувача
    user_data = UserModel(username="testuser", email="test@example.com", password="password", roles=Role.admin)
    created_user = await create_user(user_data, db)
    assert created_user is not None
    assert created_user.email == "test@example.com"
    assert created_user.avatar is not None
    assert created_user.roles == Role.user.value

    with pytest.raises(Exception):
        await create_user(user_data, db)

@pytest.mark.asyncio
async def test_update_avatar(db: Session):
    # Create a user in the database
    user_data = UserModel(username="testuser", email="test@example.com", password="password", roles=Role.admin)
    created_user = await create_user(user_data, db)

    # Test case for updating the avatar
    new_avatar_url = "https://example.com/new_avatar.jpg"
    updated_user = await update_avatar("test@example.com", new_avatar_url, db)
    assert updated_user is not None
    assert updated_user.avatar == new_avatar_url

    # Test case for updating the avatar of a non-existent user
    with pytest.raises(Exception):
        await update_avatar("nonexistent@example.com", new_avatar_url, db)

@pytest.mark.asyncio
async def test_update_token(db: Session):
    # Create a user in the database
    user_data = UserModel(username="testuser", email="test@example.com", password="password", roles=Role.admin)
    created_user = await create_user(user_data, db)

    # Test case for updating the token
    new_refresh_token = "new_refresh_token"
    await update_token(created_user, new_refresh_token, db)
    updated_user = await get_user_by_email("test@example.com", db)
    assert updated_user is not None
    assert updated_user.refresh_token == new_refresh_token

    # Test case for updating the token of a non-existent user
    with pytest.raises(Exception):
        await update_token(None, new_refresh_token, db)

@pytest.mark.asyncio
async def test_confirmed_email(db: Session):
    # Create a user in the database
    user_data = UserModel(username="testuser", email="test@example.com", password="password", roles=Role.admin)
    created_user = await create_user(user_data, db)

    # Test case for confirming email
    await confirmed_email("test@example.com", db)
    confirmed_user = await get_user_by_email("test@example.com", db)
    assert confirmed_user is not None
    assert confirmed_user.confirmed

    # Test case for confirming email of a non-existent user
    with pytest.raises(Exception):
        await confirmed_email("nonexistent@example.com", db)
