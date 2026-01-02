"""
Database implementation using SQLAlchemy
Supports both PostgreSQL and SQLite
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.db_models import User as DBUser, Score as DBScore, GameModeEnum
from app.db_config import get_db_session, init_db
from app.models import GameMode
from passlib.context import CryptContext
from datetime import datetime

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Database:
    """Database class using SQLAlchemy"""
    
    def __init__(self, initialize_test_data: bool = False):
        """Initialize database"""
        # Initialize database tables
        init_db()
        
        # Initialize with test data if requested
        if initialize_test_data:
            try:
                self._initialize_test_data()
            except Exception as e:
                print(f"Warning: Failed to initialize test data: {e}")
    
    def _truncate_password(self, password: str) -> str:
        """Helper to truncate password to 72 bytes safely for bcrypt"""
        if not isinstance(password, str):
            password = str(password)
        
        password_bytes = password.encode('utf-8')
        
        if len(password_bytes) <= 72:
            return password
        
        # Truncate to 70 bytes (safe margin)
        max_bytes = 70
        truncated_bytes = password_bytes[:max_bytes]
        
        # Remove incomplete UTF-8 sequences
        while truncated_bytes and (truncated_bytes[-1] & 0b11000000) == 0b10000000:
            truncated_bytes = truncated_bytes[:-1]
            if len(truncated_bytes) == 0:
                truncated_bytes = password_bytes[:1]
                break
        
        result = truncated_bytes.decode('utf-8', errors='ignore')
        
        # Final verification
        while len(result.encode('utf-8')) > 72 and len(result) > 0:
            result = result[:-1]
        
        return result
    
    def hash_password(self, password: str) -> str:
        """Hash a password (bcrypt has 72 byte limit)"""
        password = self._truncate_password(password)
        
        # Final check
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 70:
            password_bytes = password_bytes[:70]
            while password_bytes and (password_bytes[-1] & 0b11000000) == 0b10000000:
                password_bytes = password_bytes[:-1]
            password = password_bytes.decode('utf-8', errors='ignore')
        
        while True:
            pwd_bytes = password.encode('utf-8')
            if len(pwd_bytes) <= 72:
                break
            if len(password) > 0:
                password = password[:-1]
            else:
                password = "a"
                break
        
        final_pwd_bytes = password.encode('utf-8')
        if len(final_pwd_bytes) > 72:
            password = final_pwd_bytes[:70].decode('utf-8', errors='ignore')
            while len(password.encode('utf-8')) > 72 and len(password) > 0:
                password = password[:-1]
        
        try:
            return pwd_context.hash(password)
        except ValueError as e:
            if "72 bytes" in str(e):
                password = password.encode('utf-8')[:70].decode('utf-8', errors='ignore')
                while password.encode('utf-8') and (password.encode('utf-8')[-1] & 0b11000000) == 0b10000000:
                    password = password[:-1]
                return pwd_context.hash(password)
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        plain_password = self._truncate_password(plain_password)
        
        # Final check
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 70:
            password_bytes = password_bytes[:70]
            while password_bytes and (password_bytes[-1] & 0b11000000) == 0b10000000:
                password_bytes = password_bytes[:-1]
            plain_password = password_bytes.decode('utf-8', errors='ignore')
        
        while True:
            pwd_bytes = plain_password.encode('utf-8')
            if len(pwd_bytes) <= 72:
                break
            if len(plain_password) > 0:
                plain_password = plain_password[:-1]
            else:
                plain_password = "a"
                break
        
        final_pwd_bytes = plain_password.encode('utf-8')
        if len(final_pwd_bytes) > 72:
            plain_password = final_pwd_bytes[:70].decode('utf-8', errors='ignore')
            while len(plain_password.encode('utf-8')) > 72 and len(plain_password) > 0:
                plain_password = plain_password[:-1]
        
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except ValueError as e:
            if "72 bytes" in str(e):
                plain_password = plain_password.encode('utf-8')[:70].decode('utf-8', errors='ignore')
                while plain_password.encode('utf-8') and (plain_password.encode('utf-8')[-1] & 0b11000000) == 0b10000000:
                    plain_password = plain_password[:-1]
                return pwd_context.verify(plain_password, hashed_password)
            raise
    
    def create_user(self, username: str, email: str, password: str) -> int:
        """Create a new user and return user ID"""
        db = get_db_session()
        try:
            user = DBUser(
                username=username,
                email=email,
                password_hash=self.hash_password(password)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user.id
        finally:
            db.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        db = get_db_session()
        try:
            user = db.query(DBUser).filter(DBUser.id == user_id).first()
            if not user:
                return None
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "password_hash": user.password_hash
            }
        finally:
            db.close()
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        db = get_db_session()
        try:
            user = db.query(DBUser).filter(DBUser.email == email).first()
            if not user:
                return None
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "password_hash": user.password_hash
            }
        finally:
            db.close()
    
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username"""
        db = get_db_session()
        try:
            user = db.query(DBUser).filter(DBUser.username == username).first()
            if not user:
                return None
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "password_hash": user.password_hash
            }
        finally:
            db.close()
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        db = get_db_session()
        try:
            return db.query(DBUser).filter(DBUser.email == email).first() is not None
        finally:
            db.close()
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        db = get_db_session()
        try:
            return db.query(DBUser).filter(DBUser.username == username).first() is not None
        finally:
            db.close()
    
    def create_score(self, user_id: int, score: int, mode: GameMode, timestamp: Optional[datetime] = None) -> int:
        """Create a new score entry"""
        db = get_db_session()
        try:
            # Convert GameMode enum to GameModeEnum
            mode_enum = GameModeEnum.WALL if mode == GameMode.WALL else GameModeEnum.PASS
            
            score_entry = DBScore(
                user_id=user_id,
                score=score,
                mode=mode_enum,
                timestamp=timestamp or datetime.utcnow()
            )
            db.add(score_entry)
            db.commit()
            db.refresh(score_entry)
            return score_entry.id
        finally:
            db.close()
    
    def get_scores(self, limit: Optional[int] = None, mode: Optional[GameMode] = None) -> List[dict]:
        """Get scores, optionally filtered by mode and limited"""
        db = get_db_session()
        try:
            query = db.query(
                DBScore.id,
                DBScore.user_id,
                DBUser.username,
                DBScore.score,
                DBScore.mode,
                DBScore.timestamp
            ).join(DBUser, DBScore.user_id == DBUser.id)
            
            # Filter by mode if provided
            if mode:
                mode_enum = GameModeEnum.WALL if mode == GameMode.WALL else GameModeEnum.PASS
                query = query.filter(DBScore.mode == mode_enum)
            
            # Order by score descending
            query = query.order_by(desc(DBScore.score))
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            
            # Convert to dict format with rank
            scores = []
            for idx, (score_id, user_id, username, score_val, mode_val, timestamp) in enumerate(results, 1):
                scores.append({
                    "id": score_id,
                    "userId": user_id,
                    "username": username,
                    "score": score_val,
                    "mode": mode_val.value,  # Convert enum to string
                    "timestamp": int(timestamp.timestamp() * 1000),  # Convert to milliseconds
                    "rank": idx
                })
            
            return scores
        finally:
            db.close()
    
    def get_score_by_id(self, score_id: int) -> Optional[dict]:
        """Get a score by its ID"""
        db = get_db_session()
        try:
            score = db.query(
                DBScore.id,
                DBScore.user_id,
                DBUser.username,
                DBScore.score,
                DBScore.mode,
                DBScore.timestamp
            ).join(DBUser, DBScore.user_id == DBUser.id).filter(DBScore.id == score_id).first()
            
            if not score:
                return None
            
            score_id_val, user_id, username, score_val, mode_val, timestamp = score
            return {
                "id": score_id_val,
                "userId": user_id,
                "username": username,
                "score": score_val,
                "mode": mode_val.value,
                "timestamp": int(timestamp.timestamp() * 1000)
            }
        finally:
            db.close()
    
    def get_user_scores(self, user_id: int) -> List[dict]:
        """Get all scores for a specific user"""
        db = get_db_session()
        try:
            scores = db.query(DBScore).filter(DBScore.user_id == user_id).order_by(desc(DBScore.timestamp)).all()
            
            return [{
                "id": score.id,
                "userId": score.user_id,
                "username": "",  # Will be filled if needed
                "score": score.score,
                "mode": score.mode.value,
                "timestamp": int(score.timestamp.timestamp() * 1000)
            } for score in scores]
        finally:
            db.close()
    
    def _initialize_test_data(self):
        """Initialize database with test data (currently disabled)"""
        # Test data initialization removed
        pass


# Global database instance
# Initialize database tables only (no test data)
db = Database(initialize_test_data=False)
