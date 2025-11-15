#!/usr/bin/env python3
"""
BASE AGENT - Framework para todos os sub-agents
Fornece funcionalidade comum: DB connection, reporting, rollback
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import mysql.connector

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Database config
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'rootpassword',
    'database': 'lisboetas_web'
}


@dataclass
class AgentMetrics:
    """Standard metrics for all agents"""
    items_total: int = 0
    items_processed: int = 0
    items_succeeded: int = 0
    items_failed: int = 0
    items_skipped: int = 0
    errors: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.items_processed == 0:
            return 0.0
        return self.items_succeeded / self.items_processed

    @property
    def completion_rate(self) -> float:
        """Calculate completion rate"""
        if self.items_total == 0:
            return 0.0
        return self.items_processed / self.items_total


class BaseAgent:
    """Base class for all sub-agents"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.metrics = AgentMetrics()
        self.db = None
        self.start_time = datetime.now()
        self.end_time = None

        # Setup logging
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(f'[{self.name}] %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def connect_db(self):
        """Connect to WordPress database"""
        try:
            self.db = mysql.connector.connect(**DB_CONFIG, buffered=True)
            self.logger.info(f"✓ Conectado à database: {DB_CONFIG['database']}")
        except Exception as e:
            self.logger.error(f"❌ Falha conexão database: {e}")
            raise

    def disconnect_db(self):
        """Disconnect from database"""
        if self.db:
            self.db.close()
            self.logger.info("Database disconnected")

    def create_backup(self, backup_name: str) -> Optional[Path]:
        """Create database backup before making changes"""
        try:
            backup_dir = BASE_DIR / 'backups' / 'orchestrator'
            backup_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_dir / f"{backup_name}_{timestamp}.sql"

            import subprocess
            cmd = [
                'docker', 'exec', 'chapeus_mysql',
                'mysqldump',
                '-u', 'root',
                f"-p{DB_CONFIG['password']}",
                DB_CONFIG['database']
            ]

            with open(backup_file, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)

            self.logger.info(f"✓ Backup created: {backup_file}")
            return backup_file

        except Exception as e:
            self.logger.error(f"❌ Backup failed: {e}")
            return None

    def rollback_from_backup(self, backup_file: Path) -> bool:
        """Rollback database from backup"""
        try:
            if not backup_file.exists():
                self.logger.error(f"Backup file not found: {backup_file}")
                return False

            import subprocess
            cmd = [
                'docker', 'exec', '-i', 'chapeus_mysql',
                'mysql',
                '-u', 'root',
                f"-p{DB_CONFIG['password']}",
                DB_CONFIG['database']
            ]

            with open(backup_file, 'r') as f:
                subprocess.run(cmd, stdin=f, check=True)

            self.logger.info(f"✓ Rollback successful from: {backup_file}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Rollback failed: {e}")
            return False

    def log_progress(self, message: str, progress: Optional[float] = None):
        """Log progress message with optional percentage"""
        if progress is not None:
            self.logger.info(f"{message} ({progress:.1f}%)")
        else:
            self.logger.info(message)

    def add_error(self, error: str):
        """Add error to metrics"""
        self.metrics.errors.append(error)
        self.metrics.items_failed += 1
        self.logger.error(f"❌ {error}")

    def add_warning(self, warning: str):
        """Add warning to metrics"""
        self.metrics.warnings.append(warning)
        self.logger.warning(f"⚠️  {warning}")

    def record_success(self):
        """Record successful item processing"""
        self.metrics.items_succeeded += 1
        self.metrics.items_processed += 1

    def record_failure(self):
        """Record failed item processing"""
        self.metrics.items_failed += 1
        self.metrics.items_processed += 1

    def record_skip(self):
        """Record skipped item"""
        self.metrics.items_skipped += 1
        self.metrics.items_processed += 1

    def print_summary(self):
        """Print execution summary"""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        print("\n" + "="*70)
        print(f"{self.name} - SUMMARY")
        print("="*70)
        print(f"Description: {self.description}")
        print(f"Duration: {duration:.1f}s")
        print(f"\nMetrics:")
        print(f"  Total items: {self.metrics.items_total}")
        print(f"  Processed: {self.metrics.items_processed}")
        print(f"  ✅ Succeeded: {self.metrics.items_succeeded}")
        print(f"  ❌ Failed: {self.metrics.items_failed}")
        print(f"  ⊘ Skipped: {self.metrics.items_skipped}")
        print(f"\nRates:")
        print(f"  Success rate: {self.metrics.success_rate:.1%}")
        print(f"  Completion rate: {self.metrics.completion_rate:.1%}")

        if self.metrics.errors:
            print(f"\nErrors ({len(self.metrics.errors)}):")
            for error in self.metrics.errors[:5]:  # First 5
                print(f"  - {error}")
            if len(self.metrics.errors) > 5:
                print(f"  ... and {len(self.metrics.errors) - 5} more")

        if self.metrics.warnings:
            print(f"\nWarnings ({len(self.metrics.warnings)}):")
            for warning in self.metrics.warnings[:5]:  # First 5
                print(f"  - {warning}")
            if len(self.metrics.warnings) > 5:
                print(f"  ... and {len(self.metrics.warnings) - 5} more")

        print("="*70 + "\n")

    def save_results(self, output_file: Optional[Path] = None):
        """Save results to JSON file"""
        if output_file is None:
            results_dir = BASE_DIR / 'relatorios' / 'orchestrator' / 'agents'
            results_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = results_dir / f"{self.name.lower().replace('-', '_')}_{timestamp}.json"

        results = {
            'agent_name': self.name,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            'metrics': asdict(self.metrics)
        }

        output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        self.logger.info(f"Results saved: {output_file}")

    def run(self) -> int:
        """
        Main execution method - to be overridden by sub-agents
        Returns: 0 on success, 1 on failure
        """
        raise NotImplementedError("Sub-agents must implement run() method")

    def execute(self) -> int:
        """
        Execute agent with standard workflow:
        1. Connect DB
        2. Create backup
        3. Run agent logic
        4. Print summary
        5. Save results
        6. Disconnect DB
        """
        print("\n" + "="*70)
        print(f"{self.name}")
        print(f"{self.description}")
        print("="*70 + "\n")

        try:
            # Connect to database
            self.connect_db()

            # Run agent logic
            exit_code = self.run()

            # Print summary
            self.print_summary()

            # Save results
            self.save_results()

            return exit_code

        except Exception as e:
            self.logger.error(f"💥 Fatal error: {e}")
            self.add_error(f"Fatal error: {e}")
            self.print_summary()
            return 1

        finally:
            # Cleanup
            self.disconnect_db()


# Example usage in sub-agents:
"""
from orchestrator.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MyAgent-Name",
            description="What this agent does"
        )

    def run(self) -> int:
        self.metrics.items_total = 100

        for i in range(100):
            try:
                # Do work
                self.record_success()
                self.log_progress(f"Processing item {i+1}", (i+1)/100*100)
            except Exception as e:
                self.add_error(str(e))
                self.record_failure()

        # Return 0 if success rate >= threshold
        return 0 if self.metrics.success_rate >= 0.9 else 1

if __name__ == '__main__':
    agent = MyAgent()
    sys.exit(agent.execute())
"""
