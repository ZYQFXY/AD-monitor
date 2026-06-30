import os
import sys
import pytest
import sqlite3
import tempfile

# 确保项目根目录在 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture
def tmp_db(monkeypatch, tmp_path):
    """每个测试用独立的临时数据库"""
    db_file = str(tmp_path / "test.db")
    monkeypatch.setattr("config.DB_PATH", db_file)
    import importlib
    import db.database as dbmod
    importlib.reload(dbmod)
    dbmod.init_db()
    yield db_file
