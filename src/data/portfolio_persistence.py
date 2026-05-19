"""Portfolio persistence and state management."""

import json
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime

class PortfolioPersistence:
    """Save/load portfolio state to database."""
    
    def __init__(self, db_path: str = "./infrarisk.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id TEXT PRIMARY KEY,
                name TEXT,
                created_at TEXT,
                updated_at TEXT,
                data JSON,
                score INTEGER,
                status TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                portfolio_id TEXT,
                project_data JSON,
                predictions JSON,
                created_at TEXT,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulation_runs (
                id TEXT PRIMARY KEY,
                portfolio_id TEXT,
                results JSON,
                timestamp TEXT,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_portfolio(self, portfolio_id: str, name: str, projects: List[Dict], score: int = 0) -> bool:
        """Save portfolio state."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO portfolios (id, name, created_at, updated_at, data, score, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            portfolio_id,
            name,
            now,
            now,
            json.dumps(projects),
            score,
            'active'
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def load_portfolio(self, portfolio_id: str) -> Optional[Dict]:
        """Load portfolio state."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM portfolios WHERE id = ?", (portfolio_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'created_at': row[2],
                'updated_at': row[3],
                'projects': json.loads(row[4]),
                'score': row[5],
                'status': row[6],
            }
        return None
    
    def list_portfolios(self) -> List[Dict]:
        """List all portfolios."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, updated_at, score FROM portfolios ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [{'id': r[0], 'name': r[1], 'updated_at': r[2], 'score': r[3]} for r in rows]
