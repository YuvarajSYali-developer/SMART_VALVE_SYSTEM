"""
Database Seed Script
Creates default users and initial configuration
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal, init_db
from app.db.models import User, Rule, Setting
from app.utils.security import hash_password
from app.utils.logger import logger


def seed_users(db):
    """Create default users"""
    logger.info("Seeding users...")
    
    users = [
        {
            "username": "yuvarajyali@gmail",
            "password": "SMART_VALVE_SYSTEM",
            "role": "admin"
        },
        {
            "username": "admin",
            "password": "admin123",
            "role": "admin"
        },
        {
            "username": "operator",
            "password": "operator123",
            "role": "operator"
        },
        {
            "username": "viewer",
            "password": "viewer123",
            "role": "viewer"
        }
    ]
    
    for user_data in users:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if existing:
            logger.info(f"  - User '{user_data['username']}' already exists, skipping")
            continue
        
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            role=user_data["role"],
            created_at=int(time.time()),
            is_active=True
        )
        db.add(user)
        logger.info(f"  ✓ Created user: {user_data['username']} (role: {user_data['role']})")
    
    db.commit()


def seed_rules(db):
    """Create default safety rules"""
    logger.info("Seeding safety rules...")
    
    rules = [
        {
            "name": "max_pressure_threshold",
            "config": {
                "threshold": 6.0,
                "unit": "bar",
                "description": "Maximum allowed pressure before emergency shutdown"
            }
        },
        {
            "name": "critical_concentration",
            "config": {
                "threshold": 500.0,
                "unit": "units",
                "description": "Critical concentration level triggering emergency"
            }
        },
        {
            "name": "auto_close_timeout",
            "config": {
                "timeout": 1800,
                "unit": "seconds",
                "description": "Auto-close valve after this duration (30 minutes)"
            }
        },
        {
            "name": "daily_operations_limit",
            "config": {
                "limit": 20,
                "unit": "operations",
                "description": "Maximum valve operations per day"
            }
        }
    ]
    
    for rule_data in rules:
        existing = db.query(Rule).filter(Rule.name == rule_data["name"]).first()
        if existing:
            logger.info(f"  - Rule '{rule_data['name']}' already exists, skipping")
            continue
        
        rule = Rule(
            name=rule_data["name"],
            json_config=rule_data["config"],
            last_updated=int(time.time()),
            enabled=True
        )
        db.add(rule)
        logger.info(f"  ✓ Created rule: {rule_data['name']}")
    
    db.commit()


def seed_settings(db):
    """Create default settings"""
    logger.info("Seeding settings...")
    
    settings = [
        {
            "key": "system_name",
            "value": "Smart Water Valve System",
            "description": "Display name for the system"
        },
        {
            "key": "alert_retention_days",
            "value": "30",
            "description": "Number of days to retain alerts"
        },
        {
            "key": "telemetry_retention_days",
            "value": "7",
            "description": "Number of days to retain telemetry data"
        }
    ]
    
    for setting_data in settings:
        existing = db.query(Setting).filter(Setting.key == setting_data["key"]).first()
        if existing:
            logger.info(f"  - Setting '{setting_data['key']}' already exists, skipping")
            continue
        
        setting = Setting(
            key=setting_data["key"],
            value=setting_data["value"],
            description=setting_data["description"]
        )
        db.add(setting)
        logger.info(f"  ✓ Created setting: {setting_data['key']}")
    
    db.commit()


def main():
    """Main seed function"""
    logger.info("=" * 60)
    logger.info("DATABASE SEED SCRIPT")
    logger.info("=" * 60)
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    logger.info("✓ Database initialized")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Seed data
        seed_users(db)
        seed_rules(db)
        seed_settings(db)
        
        logger.info("=" * 60)
        logger.info("✅ SEED COMPLETE!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Default Users:")
        logger.info("  - yuvarajyali@gmail / SMART_VALVE_SYSTEM (admin)")
        logger.info("  - admin / admin123 (admin)")
        logger.info("  - operator / operator123 (operator)")
        logger.info("  - viewer / viewer123 (viewer)")
        logger.info("")
        logger.info("⚠️  IMPORTANT: Change default passwords in production!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
