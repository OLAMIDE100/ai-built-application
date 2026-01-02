"""
Mock database implementation using in-memory dictionaries.
This will be replaced with a real database later.
"""
from typing import Dict, List, Optional
from app.models import User, Score, GameMode
from passlib.context import CryptContext
from datetime import datetime

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class MockDatabase:
    def __init__(self, initialize_test_data: bool = True):
        # In-memory storage
        self.users: Dict[int, dict] = {}
        self.users_by_email: Dict[str, int] = {}
        self.users_by_username: Dict[str, int] = {}
        self.scores: Dict[int, dict] = {}
        self.next_user_id = 1
        self.next_score_id = 1
        
        # Initialize with some test data (can be disabled for testing)
        if initialize_test_data:
            try:
                self._initialize_test_data()
            except Exception as e:
                # If initialization fails, continue without test data
                print(f"Warning: Failed to initialize test data: {e}")
                pass
    
    def _truncate_password(self, password: str) -> str:
        """Helper to truncate password to 72 bytes safely for bcrypt"""
        # Ensure it's a string
        if not isinstance(password, str):
            password = str(password)
        
        # Convert to bytes first
        password_bytes = password.encode('utf-8')
        
        # If already <= 72 bytes, return as-is
        if len(password_bytes) <= 72:
            return password
        
        # Truncate to 70 bytes (safe margin) and remove incomplete UTF-8 sequences
        max_bytes = 70
        truncated_bytes = password_bytes[:max_bytes]
        
        # Remove any incomplete UTF-8 sequences at the end
        # UTF-8 continuation bytes (10xxxxxx) indicate we're in the middle of a character
        while truncated_bytes and (truncated_bytes[-1] & 0b11000000) == 0b10000000:
            truncated_bytes = truncated_bytes[:-1]
            if len(truncated_bytes) == 0:
                truncated_bytes = password_bytes[:1]
                break
        
        # Decode back to string
        result = truncated_bytes.decode('utf-8', errors='ignore')
        
        # Final verification: ensure result is definitely <= 72 bytes
        # Truncate character by character if needed
        while len(result.encode('utf-8')) > 72 and len(result) > 0:
            result = result[:-1]
        
        # Absolute final check - if still too long (shouldn't happen), force to 70 bytes
        final_bytes = result.encode('utf-8')
        if len(final_bytes) > 72:
            # Emergency: use first 70 bytes directly
            result = password_bytes[:70].decode('utf-8', errors='ignore')
            # Remove trailing incomplete sequences
            while len(result.encode('utf-8')) > 72 and len(result) > 0:
                result = result[:-1]
        
        return result
    
    def _initialize_test_data(self):
        """Initialize database with fake users and scores"""
        # Create fake users with various usernames
        fake_users = [
            {"username": "snake_master", "email": "snake_master@example.com", "password": "password123"},
            {"username": "gamer_pro", "email": "gamer_pro@example.com", "password": "password123"},
            {"username": "speed_demon", "email": "speed_demon@example.com", "password": "password123"},
            {"username": "wall_crusher", "email": "wall_crusher@example.com", "password": "password123"},
            {"username": "snake_queen", "email": "snake_queen@example.com", "password": "password123"},
            {"username": "high_scorer", "email": "high_scorer@example.com", "password": "password123"},
            {"username": "game_champ", "email": "game_champ@example.com", "password": "password123"},
            {"username": "snake_legend", "email": "snake_legend@example.com", "password": "password123"},
        ]
        
        # Create users and add scores
        for idx, user_data in enumerate(fake_users):
            user_id = self.create_user(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"]
            )
            
            # Add multiple scores per user with different modes and scores
            # Higher scores for earlier users to create a realistic leaderboard
            base_score = 500 - (idx * 50)
            
            # User 1: Top player with high scores
            if user_id == 1:
                self.create_score(user_id, 850, GameMode.WALL)
                self.create_score(user_id, 720, GameMode.WALL)
                self.create_score(user_id, 650, GameMode.PASS)
                self.create_score(user_id, 580, GameMode.PASS)
            # User 2: Second place
            elif user_id == 2:
                self.create_score(user_id, 750, GameMode.WALL)
                self.create_score(user_id, 680, GameMode.WALL)
                self.create_score(user_id, 620, GameMode.PASS)
            # User 3: Third place
            elif user_id == 3:
                self.create_score(user_id, 680, GameMode.PASS)
                self.create_score(user_id, 590, GameMode.WALL)
                self.create_score(user_id, 540, GameMode.PASS)
            # User 4: Good player
            elif user_id == 4:
                self.create_score(user_id, 600, GameMode.WALL)
                self.create_score(user_id, 520, GameMode.WALL)
            # User 5: Average player
            elif user_id == 5:
                self.create_score(user_id, 480, GameMode.PASS)
                self.create_score(user_id, 420, GameMode.WALL)
                self.create_score(user_id, 380, GameMode.PASS)
            # User 6: Developing player
            elif user_id == 6:
                self.create_score(user_id, 450, GameMode.WALL)
                self.create_score(user_id, 350, GameMode.PASS)
            # User 7: New player
            elif user_id == 7:
                self.create_score(user_id, 320, GameMode.WALL)
                self.create_score(user_id, 280, GameMode.PASS)
            # User 8: Beginner
            elif user_id == 8:
                self.create_score(user_id, 250, GameMode.PASS)
                self.create_score(user_id, 180, GameMode.WALL)
    
    def hash_password(self, password: str) -> str:
        """Hash a password (bcrypt has 72 byte limit)"""
        # Ensure it's a string
        if not isinstance(password, str):
            password = str(password)
        
        # Convert to bytes and ensure <= 72 bytes
        # Use a safe margin of 70 bytes to avoid edge cases
        password_bytes = password.encode('utf-8')
        
        # Truncate to 70 bytes if needed
        if len(password_bytes) > 70:
            password_bytes = password_bytes[:70]
            # Remove incomplete UTF-8 sequences
            while password_bytes and (password_bytes[-1] & 0b11000000) == 0b10000000:
                password_bytes = password_bytes[:-1]
            password = password_bytes.decode('utf-8', errors='ignore')
        
        # CRITICAL: Final check right before calling passlib
        # Keep truncating until password is definitely <= 72 bytes
        while True:
            pwd_bytes = password.encode('utf-8')
            if len(pwd_bytes) <= 72:
                break
            # Truncate one character at a time
            if len(password) > 0:
                password = password[:-1]
            else:
                # If empty, use a minimal safe value
                password = "a"
                break
        
        # One more absolute check - encode and verify byte length
        final_pwd_bytes = password.encode('utf-8')
        if len(final_pwd_bytes) > 72:
            # Emergency: force to 70 bytes
            final_pwd_bytes = final_pwd_bytes[:70]
            while final_pwd_bytes and (final_pwd_bytes[-1] & 0b11000000) == 0b10000000:
                final_pwd_bytes = final_pwd_bytes[:-1]
            password = final_pwd_bytes.decode('utf-8', errors='ignore')
        
        # Final verification - must be <= 72 bytes
        final_byte_check = password.encode('utf-8')
        if len(final_byte_check) > 72:
            # This should never happen, but if it does, force truncation
            password = final_byte_check[:70].decode('utf-8', errors='ignore')
            # Remove incomplete sequences one more time
            while len(password.encode('utf-8')) > 72 and len(password) > 0:
                password = password[:-1]
        
        # One final absolute check
        final_byte_check = password.encode('utf-8')
        if len(final_byte_check) > 72:
            # Last resort: use first 70 bytes
            password = final_byte_check[:70].decode('utf-8', errors='ignore')
        
        # Ensure password is definitely <= 72 bytes before calling passlib
        # This is a safety check to prevent the ValueError from bcrypt
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            # Force truncate to 70 bytes
            password_bytes = password_bytes[:70]
            while password_bytes and (password_bytes[-1] & 0b11000000) == 0b10000000:
                password_bytes = password_bytes[:-1]
            password = password_bytes.decode('utf-8', errors='ignore')
        
        try:
            return pwd_context.hash(password)
        except ValueError as e:
            if "72 bytes" in str(e):
                # If still too long, force to 70 bytes one more time
                password_bytes = password.encode('utf-8')[:70]
                while password_bytes and (password_bytes[-1] & 0b11000000) == 0b10000000:
                    password_bytes = password_bytes[:-1]
                password = password_bytes.decode('utf-8', errors='ignore')
                return pwd_context.hash(password)
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash (bcrypt has 72 byte limit)"""
        # Ensure it's a string
        if not isinstance(plain_password, str):
            plain_password = str(plain_password)
        
        # Convert to bytes and ensure <= 72 bytes
        # Use a safe margin of 70 bytes to avoid edge cases
        password_bytes = plain_password.encode('utf-8')
        
        # Truncate to 70 bytes if needed
        if len(password_bytes) > 70:
            password_bytes = password_bytes[:70]
            # Remove incomplete UTF-8 sequences
            while password_bytes and (password_bytes[-1] & 0b11000000) == 0b10000000:
                password_bytes = password_bytes[:-1]
            plain_password = password_bytes.decode('utf-8', errors='ignore')
        
        # CRITICAL: Final check right before calling passlib
        # Keep truncating until password is definitely <= 72 bytes
        while True:
            pwd_bytes = plain_password.encode('utf-8')
            if len(pwd_bytes) <= 72:
                break
            # Truncate one character at a time
            if len(plain_password) > 0:
                plain_password = plain_password[:-1]
            else:
                # If empty, use a minimal safe value
                plain_password = "a"
                break
        
        # One more absolute check - encode and verify byte length
        final_pwd_bytes = plain_password.encode('utf-8')
        if len(final_pwd_bytes) > 72:
            # Emergency: force to 70 bytes
            final_pwd_bytes = final_pwd_bytes[:70]
            while final_pwd_bytes and (final_pwd_bytes[-1] & 0b11000000) == 0b10000000:
                final_pwd_bytes = final_pwd_bytes[:-1]
            plain_password = final_pwd_bytes.decode('utf-8', errors='ignore')
        
        # Final verification - must be <= 72 bytes
        final_byte_check = plain_password.encode('utf-8')
        if len(final_byte_check) > 72:
            # This should never happen, but if it does, force truncation
            plain_password = final_byte_check[:70].decode('utf-8', errors='ignore')
            # Remove incomplete sequences one more time
            while len(plain_password.encode('utf-8')) > 72 and len(plain_password) > 0:
                plain_password = plain_password[:-1]
        
        # One final absolute check
        final_byte_check = plain_password.encode('utf-8')
        if len(final_byte_check) > 72:
            # Last resort: use first 70 bytes
            plain_password = final_byte_check[:70].decode('utf-8', errors='ignore')
        
        # Ensure password is definitely <= 72 bytes before calling passlib
        # This is a safety check to prevent the ValueError from bcrypt
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            # Force truncate to 70 bytes
            password_bytes = password_bytes[:70]
            while password_bytes and (password_bytes[-1] & 0b11000000) == 0b10000000:
                password_bytes = password_bytes[:-1]
            plain_password = password_bytes.decode('utf-8', errors='ignore')
        
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except ValueError as e:
            if "72 bytes" in str(e):
                # If still too long, force to 70 bytes one more time
                password_bytes = plain_password.encode('utf-8')[:70]
                while password_bytes and (password_bytes[-1] & 0b11000000) == 0b10000000:
                    password_bytes = password_bytes[:-1]
                plain_password = password_bytes.decode('utf-8', errors='ignore')
                return pwd_context.verify(plain_password, hashed_password)
            raise
    
    def create_user(self, username: str, email: str, password: str) -> int:
        """Create a new user and return user ID"""
        user_id = self.next_user_id
        self.next_user_id += 1
        
        user = {
            "id": user_id,
            "username": username,
            "email": email,
            "password_hash": self.hash_password(password)
        }
        
        self.users[user_id] = user
        self.users_by_email[email] = user_id
        self.users_by_username[username] = user_id
        
        return user_id
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        user_id = self.users_by_email.get(email)
        if user_id:
            return self.users.get(user_id)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username"""
        user_id = self.users_by_username.get(username)
        if user_id:
            return self.users.get(user_id)
        return None
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return email in self.users_by_email
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        return username in self.users_by_username
    
    def create_score(self, user_id: int, score: int, mode: GameMode, timestamp: Optional[int] = None) -> int:
        """Create a new score entry"""
        score_id = self.next_score_id
        self.next_score_id += 1
        
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        if timestamp is None:
            timestamp = int(datetime.now().timestamp() * 1000)
        
        score_entry = {
            "id": score_id,
            "userId": user_id,
            "username": user["username"],
            "score": score,
            "mode": mode.value,
            "timestamp": timestamp
        }
        
        self.scores[score_id] = score_entry
        return score_id
    
    def get_scores(self, limit: Optional[int] = None, mode: Optional[GameMode] = None) -> List[dict]:
        """Get scores, optionally filtered by mode and limited"""
        scores = list(self.scores.values())
        
        # Filter by mode if provided
        if mode:
            scores = [s for s in scores if s["mode"] == mode.value]
        
        # Sort by score descending
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Add rank
        for index, score in enumerate(scores, start=1):
            score["rank"] = index
        
        # Apply limit
        if limit:
            scores = scores[:limit]
        
        return scores
    
    def get_user_scores(self, user_id: int) -> List[dict]:
        """Get all scores for a specific user"""
        return [s for s in self.scores.values() if s["userId"] == user_id]


# Global database instance
# Initialize with fake data for development/demo purposes
# Set initialize_test_data=False for testing to avoid conflicts
db = MockDatabase(initialize_test_data=True)

