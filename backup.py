
import sqlite3
import shutil
import os
from datetime import datetime
import logging

logger = logging.getLogger('iRama')

def create_backup():
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        backup_path = os.path.join(backup_dir, f'irama_backup_{timestamp}.db')
        shutil.copy2('irama.db', backup_path)
        logger.info(f"Database backup created: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        return False

def restore_backup(backup_file):
    try:
        if not os.path.exists(backup_file):
            raise FileNotFoundError("Backup file not found")
            
        shutil.copy2(backup_file, 'irama.db')
        logger.info(f"Database restored from: {backup_file}")
        return True
    except Exception as e:
        logger.error(f"Restore failed: {str(e)}")
        return False
