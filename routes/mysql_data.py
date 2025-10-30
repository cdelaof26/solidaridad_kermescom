from flaskext.mysql import MySQL
from pathlib import Path

SESSION_TOKEN_HEADER = "Session-Token"
USER_ID_HEADER = "User-Id"
mysql: MySQL | None = None
pdir: Path | None = None
approval_pdir: Path | None = None
