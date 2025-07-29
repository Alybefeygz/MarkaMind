# MarkaMind Testing Strategy

## Genel Bakış

MarkaMind platformu için kapsamlı test stratejisi, piramidal test yaklaşımı kullanarak kod kalitesi, güvenilirlik ve performansı garanti eder. Bu strateji unit testlerden E2E testlere kadar tüm test seviyelerini kapsar.

## Test Piramidi

```
                    E2E Tests
                  ▲ (UI, API, Database)
                 ▲ ▲ (Slow, Expensive)
                ▲ ▲ ▲
               ▲ ▲ ▲ ▲ Integration Tests
              ▲ ▲ ▲ ▲ ▲ (Services, Database, External APIs)
             ▲ ▲ ▲ ▲ ▲ ▲ (Medium Speed)
            ▲ ▲ ▲ ▲ ▲ ▲ ▲
           ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ Unit Tests
          ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ (Fast, Isolated, Mocked)
         ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ (70% of tests)
```

## 1. Unit Test Patterns

### 1.1 Test Configuration

```python
# conftest.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.config.database import get_db, Base
from app.models.user import User
from app.core.security import JWTManager

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def override_get_db(db_session):
    """Override the get_db dependency."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client(override_get_db):
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def jwt_token(test_user):
    """Create a JWT token for test user."""
    jwt_manager = JWTManager()
    return jwt_manager.create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )

@pytest.fixture
def auth_headers(jwt_token):
    """Create authorization headers."""
    return {"Authorization": f"Bearer {jwt_token}"}
```

### 1.2 Service Layer Unit Tests

```python
# tests/test_services/test_chatbot_service.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.chatbot_service import ChatbotService
from app.schemas.chatbot import ChatbotCreate, ChatbotUpdate
from app.models.chatbot import Chatbot

class TestChatbotService:
    
    @pytest.fixture
    def mock_repository(self):
        """Mock chatbot repository."""
        return Mock()
    
    @pytest.fixture
    def chatbot_service(self, mock_repository):
        """Create chatbot service with mocked dependencies."""
        return ChatbotService(repository=mock_repository)
    
    @pytest.mark.asyncio
    async def test_create_chatbot_success(self, chatbot_service, mock_repository):
        """Test successful chatbot creation."""
        # Arrange
        user_id = 1
        chatbot_data = ChatbotCreate(
            name="Test Chatbot",
            description="Test Description",
            category="customer_support",
            language="tr"
        )
        
        expected_chatbot = Chatbot(
            id=1,
            name="Test Chatbot",
            user_id=user_id,
            status="draft"
        )
        
        mock_repository.create.return_value = expected_chatbot
        
        # Act
        result = await chatbot_service.create_chatbot(user_id, chatbot_data)
        
        # Assert
        assert result.name == "Test Chatbot"
        assert result.user_id == user_id
        assert result.status == "draft"
        mock_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_chatbot_invalid_data(self, chatbot_service):
        """Test chatbot creation with invalid data."""
        # Arrange
        user_id = 1
        chatbot_data = ChatbotCreate(
            name="",  # Invalid empty name
            description="Test Description"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Name cannot be empty"):
            await chatbot_service.create_chatbot(user_id, chatbot_data)
    
    @pytest.mark.asyncio
    async def test_update_chatbot_success(self, chatbot_service, mock_repository):
        """Test successful chatbot update."""
        # Arrange
        chatbot_id = 1
        user_id = 1
        update_data = ChatbotUpdate(name="Updated Chatbot")
        
        existing_chatbot = Chatbot(id=chatbot_id, user_id=user_id, name="Old Name")
        updated_chatbot = Chatbot(id=chatbot_id, user_id=user_id, name="Updated Chatbot")
        
        mock_repository.get_by_user.return_value = existing_chatbot
        mock_repository.update.return_value = updated_chatbot
        
        # Act
        result = await chatbot_service.update_chatbot(chatbot_id, user_id, update_data)
        
        # Assert
        assert result.name == "Updated Chatbot"
        mock_repository.get_by_user.assert_called_once_with(chatbot_id, user_id)
        mock_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_chatbot_not_found(self, chatbot_service, mock_repository):
        """Test updating non-existent chatbot."""
        # Arrange
        chatbot_id = 999
        user_id = 1
        update_data = ChatbotUpdate(name="Updated Chatbot")
        
        mock_repository.get_by_user.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Chatbot not found"):
            await chatbot_service.update_chatbot(chatbot_id, user_id, update_data)
```

### 1.3 Repository Layer Unit Tests

```python
# tests/test_repositories/test_chatbot_repository.py
import pytest
from app.repositories.chatbot_repository import ChatbotRepository
from app.models.chatbot import Chatbot
from app.models.user import User

class TestChatbotRepository:
    
    @pytest.fixture
    def repository(self, db_session):
        """Create repository with test database session."""
        return ChatbotRepository(db_session)
    
    @pytest.fixture
    def test_chatbot(self, db_session, test_user):
        """Create test chatbot."""
        chatbot = Chatbot(
            name="Test Chatbot",
            user_id=test_user.id,
            description="Test Description",
            status="active"
        )
        db_session.add(chatbot)
        db_session.commit()
        db_session.refresh(chatbot)
        return chatbot
    
    def test_create_chatbot(self, repository, test_user):
        """Test chatbot creation."""
        # Arrange
        chatbot_data = {
            "name": "New Chatbot",
            "user_id": test_user.id,
            "description": "New Description",
            "status": "draft"
        }
        
        # Act
        result = repository.create(chatbot_data)
        
        # Assert
        assert result.name == "New Chatbot"
        assert result.user_id == test_user.id
        assert result.status == "draft"
        assert result.id is not None
    
    def test_get_by_id(self, repository, test_chatbot):
        """Test getting chatbot by ID."""
        # Act
        result = repository.get_by_id(test_chatbot.id)
        
        # Assert
        assert result is not None
        assert result.id == test_chatbot.id
        assert result.name == test_chatbot.name
    
    def test_get_by_user(self, repository, test_chatbot, test_user):
        """Test getting chatbot by user."""
        # Act
        result = repository.get_by_user(test_chatbot.id, test_user.id)
        
        # Assert
        assert result is not None
        assert result.user_id == test_user.id
    
    def test_get_by_user_wrong_owner(self, repository, test_chatbot):
        """Test getting chatbot with wrong user ID."""
        # Act
        result = repository.get_by_user(test_chatbot.id, 999)
        
        # Assert
        assert result is None
    
    def test_list_by_user(self, repository, test_user, db_session):
        """Test listing chatbots by user."""
        # Arrange - Create multiple chatbots
        for i in range(3):
            chatbot = Chatbot(
                name=f"Chatbot {i}",
                user_id=test_user.id,
                status="active"
            )
            db_session.add(chatbot)
        db_session.commit()
        
        # Act
        result = repository.list_by_user(test_user.id)
        
        # Assert
        assert len(result) >= 3  # At least 3 we created
        assert all(cb.user_id == test_user.id for cb in result)
    
    def test_update_chatbot(self, repository, test_chatbot):
        """Test updating chatbot."""
        # Arrange
        update_data = {"name": "Updated Name", "description": "Updated Description"}
        
        # Act
        result = repository.update(test_chatbot, update_data)
        
        # Assert
        assert result.name == "Updated Name"
        assert result.description == "Updated Description"
    
    def test_delete_chatbot(self, repository, test_chatbot, db_session):
        """Test deleting chatbot."""
        # Arrange
        chatbot_id = test_chatbot.id
        
        # Act
        repository.delete(test_chatbot.id)
        
        # Assert
        deleted_chatbot = db_session.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
        assert deleted_chatbot is None
```

### 1.4 API Endpoint Unit Tests

```python
# tests/test_api/test_chatbots.py
import pytest
from unittest.mock import patch, Mock
from fastapi import status

class TestChatbotAPI:
    
    def test_create_chatbot_success(self, client, auth_headers):
        """Test successful chatbot creation via API."""
        # Arrange
        chatbot_data = {
            "name": "Test Chatbot",
            "description": "Test Description",
            "category": "customer_support",
            "language": "tr"
        }
        
        # Act
        response = client.post(
            "/api/v1/chatbots/",
            json=chatbot_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Test Chatbot"
        assert data["data"]["status"] == "draft"
    
    def test_create_chatbot_unauthorized(self, client):
        """Test chatbot creation without authentication."""
        # Arrange
        chatbot_data = {
            "name": "Test Chatbot",
            "description": "Test Description"
        }
        
        # Act
        response = client.post("/api/v1/chatbots/", json=chatbot_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_chatbot_invalid_data(self, client, auth_headers):
        """Test chatbot creation with invalid data."""
        # Arrange
        chatbot_data = {
            "name": "",  # Invalid empty name
            "description": "Test Description"
        }
        
        # Act
        response = client.post(
            "/api/v1/chatbots/",
            json=chatbot_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_chatbot_success(self, client, auth_headers, test_chatbot):
        """Test getting chatbot by ID."""
        # Act
        response = client.get(
            f"/api/v1/chatbots/{test_chatbot.id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == test_chatbot.id
        assert data["data"]["name"] == test_chatbot.name
    
    def test_get_chatbot_not_found(self, client, auth_headers):
        """Test getting non-existent chatbot."""
        # Act
        response = client.get("/api/v1/chatbots/999", headers=auth_headers)
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_chatbots(self, client, auth_headers):
        """Test listing user's chatbots."""
        # Act
        response = client.get("/api/v1/chatbots/", headers=auth_headers)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "chatbots" in data["data"]
        assert "pagination" in data["data"]
    
    def test_update_chatbot(self, client, auth_headers, test_chatbot):
        """Test updating chatbot."""
        # Arrange
        update_data = {
            "name": "Updated Chatbot",
            "description": "Updated Description"
        }
        
        # Act
        response = client.put(
            f"/api/v1/chatbots/{test_chatbot.id}",
            json=update_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "updated_fields" in data["data"]
    
    def test_delete_chatbot(self, client, auth_headers, test_chatbot):
        """Test deleting chatbot."""
        # Act
        response = client.delete(
            f"/api/v1/chatbots/{test_chatbot.id}?confirm=true",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
```

## 2. Integration Test Scenarios

### 2.1 Database Integration Tests

```python
# tests/test_integration/test_database_integration.py
import pytest
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.chatbot import Chatbot
from app.models.conversation import Conversation
from app.models.message import Message

class TestDatabaseIntegration:
    
    def test_user_chatbot_relationship(self, db_session: Session):
        """Test user-chatbot relationship."""
        # Arrange
        user = User(
            email="test@example.com",
            password_hash="hashed",
            first_name="Test",
            last_name="User"
        )
        db_session.add(user)
        db_session.commit()
        
        chatbot = Chatbot(
            name="Test Chatbot",
            user_id=user.id,
            description="Test"
        )
        db_session.add(chatbot)
        db_session.commit()
        
        # Act
        db_session.refresh(user)
        
        # Assert
        assert len(user.chatbots) == 1
        assert user.chatbots[0].name == "Test Chatbot"
    
    def test_conversation_message_cascade(self, db_session: Session, test_user, test_chatbot):
        """Test conversation-message cascade deletion."""
        # Arrange
        conversation = Conversation(
            chatbot_id=test_chatbot.id,
            session_id="test-session",
            user_id="test-user"
        )
        db_session.add(conversation)
        db_session.commit()
        
        message = Message(
            conversation_id=conversation.id,
            message_type="user",
            content="Test message"
        )
        db_session.add(message)
        db_session.commit()
        
        # Act
        db_session.delete(conversation)
        db_session.commit()
        
        # Assert
        remaining_messages = db_session.query(Message).filter(
            Message.conversation_id == conversation.id
        ).all()
        assert len(remaining_messages) == 0
    
    def test_database_constraints(self, db_session: Session):
        """Test database constraints."""
        # Test unique email constraint
        user1 = User(email="test@example.com", password_hash="hash1")
        user2 = User(email="test@example.com", password_hash="hash2")
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
```

### 2.2 Service Integration Tests

```python
# tests/test_integration/test_service_integration.py
import pytest
from unittest.mock import patch, AsyncMock
from app.services.chatbot_service import ChatbotService
from app.services.training_service import TrainingService
from app.services.rag_service import RAGService

class TestServiceIntegration:
    
    @pytest.mark.asyncio
    async def test_chatbot_training_workflow(self, db_session, test_user):
        """Test complete chatbot training workflow."""
        # Arrange
        chatbot_service = ChatbotService(db_session)
        training_service = TrainingService(db_session)
        
        # Create chatbot
        chatbot = await chatbot_service.create_chatbot(
            user_id=test_user.id,
            chatbot_data={
                "name": "Test Chatbot",
                "description": "Test"
            }
        )
        
        # Mock file upload
        with patch('app.services.training_service.process_pdf') as mock_pdf:
            mock_pdf.return_value = {"chunks": 10, "success": True}
            
            # Act - Train chatbot
            result = await training_service.train_with_pdf(
                chatbot_id=chatbot.id,
                file_path="/test/file.pdf"
            )
        
        # Assert
        assert result["success"] is True
        assert result["chunks"] == 10
    
    @pytest.mark.asyncio
    async def test_rag_embedding_integration(self, db_session, test_chatbot):
        """Test RAG embedding creation integration."""
        # Arrange
        rag_service = RAGService(db_session)
        
        with patch('app.services.rag_service.create_embedding') as mock_embedding:
            mock_embedding.return_value = [0.1] * 1536  # Mock embedding vector
            
            # Act
            result = await rag_service.create_embeddings(
                chatbot_id=test_chatbot.id,
                chunks=["Test chunk 1", "Test chunk 2"]
            )
        
        # Assert
        assert result["embeddings_created"] == 2
        assert len(result["chunk_ids"]) == 2
```

### 2.3 API Integration Tests

```python
# tests/test_integration/test_api_integration.py
import pytest
from fastapi.testclient import TestClient

class TestAPIIntegration:
    
    def test_authentication_flow(self, client: TestClient, test_user):
        """Test complete authentication flow."""
        # Login
        login_data = {
            "email": test_user.email,
            "password": "test_password"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        tokens = response.json()["data"]
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # Use access token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 200
    
    def test_chatbot_crud_flow(self, client: TestClient, auth_headers):
        """Test complete CRUD flow for chatbots."""
        # Create chatbot
        create_data = {
            "name": "Integration Test Bot",
            "description": "Test Description"
        }
        
        response = client.post("/api/v1/chatbots/", json=create_data, headers=auth_headers)
        assert response.status_code == 201
        
        chatbot_id = response.json()["data"]["chatbot_id"]
        
        # Read chatbot
        response = client.get(f"/api/v1/chatbots/{chatbot_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Update chatbot
        update_data = {"name": "Updated Bot Name"}
        response = client.put(
            f"/api/v1/chatbots/{chatbot_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Delete chatbot
        response = client.delete(
            f"/api/v1/chatbots/{chatbot_id}?confirm=true",
            headers=auth_headers
        )
        assert response.status_code == 200
```

## 3. End-to-End (E2E) Test Scenarios

### 3.1 E2E Test Configuration

```python
# tests/test_e2e/conftest.py
import pytest
import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

@pytest.fixture(scope="session")
async def browser():
    """Create browser instance for E2E tests."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        yield browser
        await browser.close()

@pytest.fixture
async def context(browser: Browser):
    """Create browser context."""
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="tr-TR",
        timezone_id="Europe/Istanbul"
    )
    yield context
    await context.close()

@pytest.fixture
async def page(context: BrowserContext):
    """Create page instance."""
    page = await context.new_page()
    yield page
    await page.close()

@pytest.fixture
async def authenticated_page(page: Page, test_user):
    """Create authenticated page."""
    # Navigate to login page
    await page.goto("http://localhost:3000/login")
    
    # Fill login form
    await page.fill('[data-testid="email-input"]', test_user.email)
    await page.fill('[data-testid="password-input"]', "test_password")
    await page.click('[data-testid="login-button"]')
    
    # Wait for navigation to dashboard
    await page.wait_for_url("**/dashboard")
    
    return page
```

### 3.2 User Journey E2E Tests

```python
# tests/test_e2e/test_user_journeys.py
import pytest
from playwright.async_api import Page, expect

class TestUserJourneys:
    
    @pytest.mark.e2e
    async def test_user_registration_flow(self, page: Page):
        """Test complete user registration flow."""
        # Navigate to registration page
        await page.goto("http://localhost:3000/register")
        
        # Fill registration form
        await page.fill('[data-testid="first-name-input"]', "Test")
        await page.fill('[data-testid="last-name-input"]', "User")
        await page.fill('[data-testid="email-input"]', "testuser@example.com")
        await page.fill('[data-testid="company-input"]', "Test Company")
        await page.fill('[data-testid="password-input"]', "SecurePass123!")
        await page.fill('[data-testid="confirm-password-input"]', "SecurePass123!")
        
        # Submit form
        await page.click('[data-testid="register-button"]')
        
        # Verify success message
        await expect(page.locator('[data-testid="success-message"]')).to_be_visible()
        await expect(page.locator('[data-testid="success-message"]')).to_contain_text(
            "Registration successful"
        )
    
    @pytest.mark.e2e
    async def test_chatbot_creation_flow(self, authenticated_page: Page):
        """Test complete chatbot creation flow."""
        page = authenticated_page
        
        # Navigate to chatbot creation
        await page.click('[data-testid="create-chatbot-button"]')
        
        # Fill chatbot form
        await page.fill('[data-testid="chatbot-name-input"]', "E2E Test Bot")
        await page.fill('[data-testid="chatbot-description-input"]', "E2E Test Description")
        await page.select_option('[data-testid="category-select"]', "customer_support")
        await page.select_option('[data-testid="language-select"]', "tr")
        
        # Submit form
        await page.click('[data-testid="create-button"]')
        
        # Verify chatbot creation
        await expect(page.locator('[data-testid="chatbot-card"]')).to_be_visible()
        await expect(page.locator('[data-testid="chatbot-name"]')).to_contain_text("E2E Test Bot")
    
    @pytest.mark.e2e
    async def test_chatbot_training_flow(self, authenticated_page: Page):
        """Test chatbot training with file upload."""
        page = authenticated_page
        
        # Navigate to existing chatbot
        await page.click('[data-testid="chatbot-card"]:first-child')
        await page.click('[data-testid="training-tab"]')
        
        # Upload training file
        file_input = page.locator('[data-testid="file-upload-input"]')
        await file_input.set_input_files("tests/fixtures/sample_training.pdf")
        
        # Start training
        await page.click('[data-testid="start-training-button"]')
        
        # Wait for training to complete
        await expect(page.locator('[data-testid="training-status"]')).to_contain_text(
            "completed", timeout=30000
        )
        
        # Verify training results
        await expect(page.locator('[data-testid="chunks-count"]')).to_be_visible()
        await expect(page.locator('[data-testid="embeddings-count"]')).to_be_visible()
    
    @pytest.mark.e2e
    async def test_chat_interaction_flow(self, authenticated_page: Page):
        """Test chat interaction with trained chatbot."""
        page = authenticated_page
        
        # Navigate to chat interface
        await page.click('[data-testid="chatbot-card"]:first-child')
        await page.click('[data-testid="test-chat-button"]')
        
        # Send a message
        await page.fill('[data-testid="message-input"]', "Merhaba, nasılsınız?")
        await page.click('[data-testid="send-button"]')
        
        # Verify user message appears
        await expect(page.locator('[data-testid="user-message"]:last-child')).to_contain_text(
            "Merhaba, nasılsınız?"
        )
        
        # Wait for bot response
        await expect(page.locator('[data-testid="bot-message"]:last-child')).to_be_visible(
            timeout=10000
        )
        
        # Verify response contains content
        bot_message = page.locator('[data-testid="bot-message"]:last-child')
        await expect(bot_message).not_to_be_empty()
    
    @pytest.mark.e2e
    async def test_analytics_dashboard_flow(self, authenticated_page: Page):
        """Test analytics dashboard functionality."""
        page = authenticated_page
        
        # Navigate to analytics
        await page.click('[data-testid="analytics-nav"]')
        
        # Verify analytics widgets load
        await expect(page.locator('[data-testid="total-conversations"]')).to_be_visible()
        await expect(page.locator('[data-testid="total-messages"]')).to_be_visible()
        await expect(page.locator('[data-testid="satisfaction-score"]')).to_be_visible()
        
        # Test date range selector
        await page.click('[data-testid="date-range-selector"]')
        await page.click('[data-testid="last-30-days"]')
        
        # Verify charts update
        await expect(page.locator('[data-testid="conversations-chart"]')).to_be_visible()
        await expect(page.locator('[data-testid="response-time-chart"]')).to_be_visible()
```

### 3.3 Cross-Browser E2E Tests

```python
# tests/test_e2e/test_cross_browser.py
import pytest
from playwright.async_api import async_playwright

@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
@pytest.mark.e2e
async def test_cross_browser_compatibility(browser_name: str):
    """Test application works across different browsers."""
    async with async_playwright() as p:
        browser = await getattr(p, browser_name).launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to app
            await page.goto("http://localhost:3000")
            
            # Verify page loads
            await page.wait_for_selector('[data-testid="main-content"]')
            
            # Test basic functionality
            await page.click('[data-testid="login-link"]')
            await page.wait_for_selector('[data-testid="login-form"]')
            
            # Verify form elements are interactive
            email_input = page.locator('[data-testid="email-input"]')
            await email_input.fill("test@example.com")
            filled_value = await email_input.input_value()
            assert filled_value == "test@example.com"
            
        finally:
            await browser.close()
```

## 4. Performance Testing

### 4.1 Load Testing

```python
# tests/test_performance/test_load.py
import asyncio
import aiohttp
import time
from typing import List, Dict
import pytest

class LoadTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request and measure response time."""
        start_time = time.time()
        
        try:
            async with self.session.request(
                method, 
                f"{self.base_url}{endpoint}", 
                **kwargs
            ) as response:
                end_time = time.time()
                content = await response.text()
                
                return {
                    "status": response.status,
                    "response_time": end_time - start_time,
                    "content_length": len(content),
                    "success": 200 <= response.status < 400
                }
        except Exception as e:
            end_time = time.time()
            return {
                "status": 0,
                "response_time": end_time - start_time,
                "content_length": 0,
                "success": False,
                "error": str(e)
            }
    
    async def concurrent_requests(
        self, 
        method: str, 
        endpoint: str, 
        concurrent_users: int,
        requests_per_user: int,
        **kwargs
    ) -> List[Dict]:
        """Run concurrent requests simulation."""
        
        async def user_session():
            results = []
            for _ in range(requests_per_user):
                result = await self.make_request(method, endpoint, **kwargs)
                results.append(result)
                await asyncio.sleep(0.1)  # Small delay between requests
            return results
        
        # Create concurrent user sessions
        tasks = [user_session() for _ in range(concurrent_users)]
        user_results = await asyncio.gather(*tasks)
        
        # Flatten results
        all_results = []
        for user_result in user_results:
            all_results.extend(user_result)
        
        return all_results

@pytest.mark.performance
class TestLoadPerformance:
    
    @pytest.mark.asyncio
    async def test_api_load_chatbot_list(self):
        """Test API load for chatbot listing."""
        async with LoadTester("http://localhost:8000") as tester:
            # Simulate 50 concurrent users making 10 requests each
            results = await tester.concurrent_requests(
                method="GET",
                endpoint="/api/v1/chatbots/",
                concurrent_users=50,
                requests_per_user=10,
                headers={"Authorization": "Bearer test_token"}
            )
            
            # Analyze results
            successful_requests = [r for r in results if r["success"]]
            failed_requests = [r for r in results if not r["success"]]
            
            success_rate = len(successful_requests) / len(results)
            avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
            p95_response_time = sorted([r["response_time"] for r in successful_requests])[int(len(successful_requests) * 0.95)]
            
            # Assertions
            assert success_rate >= 0.95, f"Success rate {success_rate} below 95%"
            assert avg_response_time <= 2.0, f"Average response time {avg_response_time}s above 2s"
            assert p95_response_time <= 5.0, f"P95 response time {p95_response_time}s above 5s"
    
    @pytest.mark.asyncio
    async def test_chat_message_load(self):
        """Test load on chat message endpoint."""
        async with LoadTester("http://localhost:8000") as tester:
            message_data = {
                "message": "Test message for load testing",
                "session_id": "load_test_session",
                "user_id": "load_test_user"
            }
            
            results = await tester.concurrent_requests(
                method="POST",
                endpoint="/api/v1/chat/1/message",
                concurrent_users=20,
                requests_per_user=5,
                json=message_data,
                headers={"Authorization": "Bearer test_token"}
            )
            
            # Analyze chat-specific metrics
            successful_requests = [r for r in results if r["success"]]
            avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
            
            # Chat responses should be faster
            assert avg_response_time <= 3.0, f"Chat response time {avg_response_time}s above 3s"
```

### 4.2 Stress Testing

```python
# tests/test_performance/test_stress.py
import pytest
import asyncio
import psutil
import time
from tests.test_performance.test_load import LoadTester

@pytest.mark.stress
class TestStressPerformance:
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage during high load."""
        initial_memory = psutil.virtual_memory().percent
        
        async with LoadTester("http://localhost:8000") as tester:
            # High load test
            results = await tester.concurrent_requests(
                method="GET",
                endpoint="/api/v1/chatbots/",
                concurrent_users=100,
                requests_per_user=20
            )
            
            peak_memory = psutil.virtual_memory().percent
            memory_increase = peak_memory - initial_memory
            
            # Memory should not increase excessively
            assert memory_increase <= 30, f"Memory usage increased by {memory_increase}%"
    
    @pytest.mark.asyncio
    async def test_database_connection_pool(self):
        """Test database connection pool under stress."""
        async with LoadTester("http://localhost:8000") as tester:
            # Simulate many database-heavy requests
            tasks = []
            for _ in range(200):  # 200 concurrent requests
                task = tester.make_request(
                    "GET", 
                    "/api/v1/analytics/1/conversations"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check for connection pool exhaustion
            successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
            error_results = [r for r in results if not isinstance(r, dict) or not r.get("success")]
            
            success_rate = len(successful_results) / len(results)
            assert success_rate >= 0.90, f"Success rate {success_rate} indicates connection pool issues"
```

## 5. RAG System Test Methodology

### 5.1 RAG Component Unit Tests

```python
# tests/test_rag/test_rag_components.py
import pytest
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from app.services.rag_service import RAGService
from app.models.rag_chunk import RAGChunk
from app.models.rag_embedding import RAGEmbedding

class TestRAGComponents:
    
    @pytest.fixture
    def mock_embedding_model(self):
        """Mock embedding model."""
        with patch('app.services.rag_service.create_embedding') as mock:
            mock.return_value = [0.1] * 1536  # Mock 1536-dimensional vector
            yield mock
    
    @pytest.fixture
    def rag_service(self, db_session):
        """Create RAG service instance."""
        return RAGService(db_session)
    
    @pytest.mark.asyncio
    async def test_text_chunking(self, rag_service):
        """Test text chunking functionality."""
        # Arrange
        long_text = "This is a test document. " * 100  # 2500+ characters
        
        # Act
        chunks = rag_service.create_chunks(long_text)
        
        # Assert
        assert len(chunks) > 1, "Long text should be split into multiple chunks"
        assert all(len(chunk) <= 1200 for chunk in chunks), "Chunks should respect size limit"
        
        # Test overlap
        if len(chunks) > 1:
            # Check that consecutive chunks have some overlap
            chunk1_end = chunks[0][-100:]  # Last 100 chars of first chunk
            chunk2_start = chunks[1][:100]  # First 100 chars of second chunk
            assert any(word in chunk2_start for word in chunk1_end.split()), "Chunks should have overlap"
    
    @pytest.mark.asyncio
    async def test_embedding_creation(self, rag_service, mock_embedding_model):
        """Test embedding creation."""
        # Arrange
        text = "This is a test chunk for embedding."
        
        # Act
        embedding = await rag_service.create_embedding(text)
        
        # Assert
        assert len(embedding) == 1536, "Embedding should have correct dimensions"
        assert all(isinstance(x, float) for x in embedding), "Embedding should contain floats"
        mock_embedding_model.assert_called_once_with(text)
    
    @pytest.mark.asyncio
    async def test_similarity_search(self, rag_service, db_session, test_chatbot):
        """Test similarity search functionality."""
        # Arrange - Create test chunks and embeddings
        test_chunks = [
            {
                "text": "Python programming language tutorial",
                "embedding": [0.8, 0.2] + [0.0] * 1534
            },
            {
                "text": "JavaScript web development guide",
                "embedding": [0.2, 0.8] + [0.0] * 1534
            },
            {
                "text": "Machine learning with Python",
                "embedding": [0.7, 0.3] + [0.0] * 1534
            }
        ]
        
        # Store test chunks
        for i, chunk_data in enumerate(test_chunks):
            chunk = RAGChunk(
                chatbot_id=test_chatbot.id,
                training_data_id=1,
                chunk_index=i,
                text=chunk_data["text"],
                text_hash=f"hash_{i}",
                source_type="test",
                chunk_size=len(chunk_data["text"])
            )
            db_session.add(chunk)
            db_session.flush()
            
            embedding = RAGEmbedding(
                chunk_id=chunk.id,
                embedding=chunk_data["embedding"],
                model="test-model",
                dimension=1536
            )
            db_session.add(embedding)
        
        db_session.commit()
        
        # Act - Search for Python-related content
        query_embedding = [0.9, 0.1] + [0.0] * 1534  # Similar to Python chunks
        
        results = await rag_service.similarity_search(
            chatbot_id=test_chatbot.id,
            query_embedding=query_embedding,
            top_k=2,
            similarity_threshold=0.5
        )
        
        # Assert
        assert len(results) >= 1, "Should find similar chunks"
        assert "Python" in results[0]["text"], "Most similar chunk should contain Python"
        assert results[0]["similarity_score"] > 0.5, "Similarity score should be above threshold"
    
    def test_chunk_deduplication(self, rag_service, db_session, test_chatbot):
        """Test chunk deduplication logic."""
        # Arrange - Create duplicate chunks
        duplicate_text = "This is a duplicate chunk for testing."
        
        chunk1 = RAGChunk(
            chatbot_id=test_chatbot.id,
            training_data_id=1,
            chunk_index=0,
            text=duplicate_text,
            text_hash=rag_service.generate_text_hash(duplicate_text),
            source_type="test",
            chunk_size=len(duplicate_text)
        )
        
        chunk2 = RAGChunk(
            chatbot_id=test_chatbot.id,
            training_data_id=2,
            chunk_index=0,
            text=duplicate_text,
            text_hash=rag_service.generate_text_hash(duplicate_text),
            source_type="test",
            chunk_size=len(duplicate_text)
        )
        
        db_session.add_all([chunk1, chunk2])
        db_session.commit()
        
        # Act
        duplicates = rag_service.find_duplicate_chunks(test_chatbot.id)
        
        # Assert
        assert len(duplicates) > 0, "Should detect duplicate chunks"
        assert duplicates[0]["text_hash"] == rag_service.generate_text_hash(duplicate_text)
```

### 5.2 RAG Quality Tests

```python
# tests/test_rag/test_rag_quality.py
import pytest
from typing import List, Dict
from app.services.rag_service import RAGService

class TestRAGQuality:
    
    @pytest.fixture
    def quality_test_data(self):
        """Quality test data with known correct answers."""
        return [
            {
                "documents": [
                    "MarkaMind platformu yapay zeka destekli chatbot hizmeti sunar.",
                    "Chatbot'lar PDF, metin ve web sayfalarından eğitilebilir.",
                    "Platform 7/24 müşteri desteği sağlar.",
                    "Aylık paket fiyatı 99 TL'den başlar."
                ],
                "questions": [
                    {
                        "question": "MarkaMind ne tür hizmet sunar?",
                        "expected_keywords": ["yapay zeka", "chatbot", "hizmet"],
                        "relevant_doc_indices": [0]
                    },
                    {
                        "question": "Chatbot'lar nasıl eğitilir?",
                        "expected_keywords": ["PDF", "metin", "web", "eğitil"],
                        "relevant_doc_indices": [1]
                    },
                    {
                        "question": "Fiyatlandırma nasıl?",
                        "expected_keywords": ["99", "TL", "aylık", "paket"],
                        "relevant_doc_indices": [3]
                    }
                ]
            }
        ]
    
    @pytest.mark.asyncio
    async def test_retrieval_relevance(self, rag_service, quality_test_data, test_chatbot):
        """Test if retrieved chunks are relevant to queries."""
        
        for test_case in quality_test_data:
            # Setup test documents
            await self._setup_test_documents(
                rag_service, 
                test_chatbot.id, 
                test_case["documents"]
            )
            
            # Test each question
            for question_data in test_case["questions"]:
                # Act
                results = await rag_service.semantic_search(
                    chatbot_id=test_chatbot.id,
                    query=question_data["question"],
                    top_k=3
                )
                
                # Assert relevance
                assert len(results) > 0, f"No results for question: {question_data['question']}"
                
                # Check if expected keywords are in results
                top_result_text = results[0]["text"].lower()
                expected_keywords = question_data["expected_keywords"]
                
                keyword_matches = sum(
                    1 for keyword in expected_keywords 
                    if keyword.lower() in top_result_text
                )
                
                relevance_score = keyword_matches / len(expected_keywords)
                assert relevance_score >= 0.5, (
                    f"Low relevance for question '{question_data['question']}'. "
                    f"Expected keywords: {expected_keywords}, "
                    f"Top result: {top_result_text}"
                )
    
    @pytest.mark.asyncio
    async def test_retrieval_ranking(self, rag_service, quality_test_data, test_chatbot):
        """Test if more relevant chunks are ranked higher."""
        
        for test_case in quality_test_data:
            await self._setup_test_documents(
                rag_service, 
                test_chatbot.id, 
                test_case["documents"]
            )
            
            for question_data in test_case["questions"]:
                results = await rag_service.semantic_search(
                    chatbot_id=test_chatbot.id,
                    query=question_data["question"],
                    top_k=len(test_case["documents"])
                )
                
                # Check if similarity scores are in descending order
                similarity_scores = [r["similarity_score"] for r in results]
                assert similarity_scores == sorted(similarity_scores, reverse=True), (
                    "Results should be ranked by similarity score"
                )
                
                # Check if most relevant document is in top results
                relevant_indices = question_data.get("relevant_doc_indices", [])
                if relevant_indices:
                    # Find positions of relevant documents in results
                    relevant_positions = []
                    for i, result in enumerate(results):
                        if any(
                            test_case["documents"][idx] in result["text"] 
                            for idx in relevant_indices
                        ):
                            relevant_positions.append(i)
                    
                    # Most relevant should be in top 2 results
                    assert min(relevant_positions) < 2, (
                        f"Most relevant document not in top 2 for: {question_data['question']}"
                    )
    
    async def _setup_test_documents(
        self, 
        rag_service: RAGService, 
        chatbot_id: int, 
        documents: List[str]
    ):
        """Helper to setup test documents in RAG system."""
        for i, doc in enumerate(documents):
            await rag_service.process_training_data(
                chatbot_id=chatbot_id,
                data_id=f"test_doc_{i}",
                content=doc,
                source_type="test"
            )
```

### 5.3 RAG Performance Tests

```python
# tests/test_rag/test_rag_performance.py
import pytest
import time
import asyncio
from app.services.rag_service import RAGService

class TestRAGPerformance:
    
    @pytest.mark.asyncio
    async def test_embedding_creation_performance(self, rag_service):
        """Test embedding creation performance."""
        # Test single embedding
        start_time = time.time()
        await rag_service.create_embedding("Test text for performance")
        single_time = time.time() - start_time
        
        assert single_time < 2.0, f"Single embedding took {single_time}s, should be under 2s"
        
        # Test batch embedding
        texts = ["Test text " + str(i) for i in range(10)]
        start_time = time.time()
        
        tasks = [rag_service.create_embedding(text) for text in texts]
        await asyncio.gather(*tasks)
        
        batch_time = time.time() - start_time
        avg_time = batch_time / len(texts)
        
        assert avg_time < 1.0, f"Batch embedding average {avg_time}s, should be under 1s"
    
    @pytest.mark.asyncio
    async def test_similarity_search_performance(self, rag_service, test_chatbot, db_session):
        """Test similarity search performance with large dataset."""
        # Create many test chunks
        num_chunks = 1000
        
        for i in range(num_chunks):
            chunk_data = {
                "chatbot_id": test_chatbot.id,
                "data_id": f"perf_test_{i}",
                "content": f"Performance test document {i} with relevant content about topic {i % 10}",
                "source_type": "test"
            }
            
            await rag_service.process_training_data(**chunk_data)
        
        # Test search performance
        start_time = time.time()
        results = await rag_service.semantic_search(
            chatbot_id=test_chatbot.id,
            query="relevant content about topic",
            top_k=10
        )
        search_time = time.time() - start_time
        
        assert search_time < 1.0, f"Search took {search_time}s, should be under 1s"
        assert len(results) == 10, "Should return requested number of results"
    
    @pytest.mark.asyncio
    async def test_concurrent_search_performance(self, rag_service, test_chatbot):
        """Test performance under concurrent search load."""
        # Setup some test data
        for i in range(100):
            await rag_service.process_training_data(
                chatbot_id=test_chatbot.id,
                data_id=f"concurrent_test_{i}",
                content=f"Test document {i} with searchable content",
                source_type="test"
            )
        
        # Test concurrent searches
        queries = [f"searchable content {i}" for i in range(20)]
        
        start_time = time.time()
        tasks = [
            rag_service.semantic_search(
                chatbot_id=test_chatbot.id,
                query=query,
                top_k=5
            )
            for query in queries
        ]
        
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        avg_time = total_time / len(queries)
        assert avg_time < 0.5, f"Concurrent search average {avg_time}s, should be under 0.5s"
        assert all(len(result) <= 5 for result in results), "All searches should return results"
```

### 5.4 RAG Integration Tests

```python
# tests/test_rag/test_rag_integration.py
import pytest
from app.services.rag_service import RAGService
from app.services.chatbot_service import ChatbotService

class TestRAGIntegration:
    
    @pytest.mark.asyncio
    async def test_end_to_end_rag_workflow(self, db_session, test_user):
        """Test complete RAG workflow from training to response generation."""
        # Create services
        chatbot_service = ChatbotService(db_session)
        rag_service = RAGService(db_session)
        
        # 1. Create chatbot
        chatbot = await chatbot_service.create_chatbot(
            user_id=test_user.id,
            chatbot_data={
                "name": "RAG Test Bot",
                "description": "Testing RAG integration"
            }
        )
        
        # 2. Add training data
        training_content = """
        MarkaMind Sıkça Sorulan Sorular:
        
        Soru: Çalışma saatleriniz nedir?
        Cevap: Hafta içi 09:00-18:00 arası hizmet veriyoruz.
        
        Soru: İade politikanız nasıl?
        Cevap: 14 gün içinde koşulsuz iade yapabilirsiniz.
        
        Soru: Ödeme seçenekleri neler?
        Cevap: Kredi kartı, banka kartı ve havale ile ödeme yapabilirsiniz.
        """
        
        await rag_service.process_training_data(
            chatbot_id=chatbot.id,
            data_id="faq_data",
            content=training_content,
            source_type="manual"
        )
        
        # 3. Test retrieval
        search_results = await rag_service.semantic_search(
            chatbot_id=chatbot.id,
            query="Çalışma saatleri nedir?",
            top_k=3
        )
        
        assert len(search_results) > 0, "Should find relevant content"
        assert "09:00-18:00" in search_results[0]["text"], "Should find working hours"
        
        # 4. Test response generation
        response = await rag_service.generate_response(
            chatbot_id=chatbot.id,
            user_query="Kaçta açıksınız?",
            chat_history=[]
        )
        
        assert "09:00" in response["response"] or "18:00" in response["response"], (
            "Response should include working hours"
        )
        assert len(response["sources"]) > 0, "Response should include source information"
        assert response["confidence"] > 0.5, "Response should have reasonable confidence"
    
    @pytest.mark.asyncio
    async def test_rag_with_multiple_data_sources(self, rag_service, test_chatbot):
        """Test RAG with multiple data source types."""
        # Add different types of training data
        data_sources = [
            {
                "data_id": "pdf_data",
                "content": "PDF kaynaklı bilgi: Ürün kılavuzu ve kullanım talimatları.",
                "source_type": "pdf"
            },
            {
                "data_id": "web_data", 
                "content": "Web sitesi bilgisi: Online destek ve SSS sayfası.",
                "source_type": "url"
            },
            {
                "data_id": "manual_data",
                "content": "Manuel girdi: Özel müşteri hizmetleri bilgileri.",
                "source_type": "manual"
            }
        ]
        
        for data in data_sources:
            await rag_service.process_training_data(
                chatbot_id=test_chatbot.id,
                **data
            )
        
        # Test filtered search by source type
        pdf_results = await rag_service.semantic_search(
            chatbot_id=test_chatbot.id,
            query="ürün kılavuzu",
            filters={"source_type": ["pdf"]}
        )
        
        assert len(pdf_results) > 0, "Should find PDF source results"
        assert all(r["source_type"] == "pdf" for r in pdf_results), "Should only return PDF sources"
        
        # Test mixed source search
        mixed_results = await rag_service.semantic_search(
            chatbot_id=test_chatbot.id,
            query="bilgi destek",
            top_k=5
        )
        
        source_types = set(r["source_type"] for r in mixed_results)
        assert len(source_types) > 1, "Should return multiple source types"
```

Bu test stratejisi, MarkaMind platformunun tüm bileşenlerinin kaliteli, güvenilir ve performanslı çalışmasını garanti edecek kapsamlı bir test altyapısı sağlar.