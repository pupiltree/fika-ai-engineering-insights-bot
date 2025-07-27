from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

Base = declarative_base()

class Commit(Base):
    __tablename__ = "commits"
    id = Column(Integer, primary_key=True)
    sha = Column(String, unique=True)
    author = Column(String)
    date = Column(DateTime)
    additions = Column(Integer)
    deletions = Column(Integer)
    files_changed = Column(Integer)

class PR(Base):
    __tablename__ = "prs"
    id = Column(Integer, primary_key=True)
    number = Column(Integer, unique=True)
    author = Column(String)
    created_at = Column(DateTime)
    closed_at = Column(DateTime, nullable=True)
    state = Column(String)
    reviewers = Column(String, nullable=True)  # ✅ NEW FIELD

class Database:
    def __init__(self):
        self.engine = create_engine("sqlite:///data/fika.db")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def store_commit(self, data):
        session = self.Session()
        try:
            commit = Commit(
                sha=data.get("sha"),
                author=data.get("commit", {}).get("author", {}).get("name", "Unknown"),
                date=datetime.fromisoformat(
                    data.get("commit", {}).get("date", datetime.now().isoformat()).replace("Z", "+00:00")
                ),
                additions=data.get("stats", {}).get("additions", 0),
                deletions=data.get("stats", {}).get("deletions", 0),
                files_changed=len(data.get("files", []))
            )
            session.merge(commit)
            session.commit()
        finally:
            session.close()

    def store_pr(self, data):
        session = self.Session()
        try:
            reviewers = data.get("reviewers")
            if isinstance(reviewers, list):
                reviewers = ",".join(reviewers)  # ✅ Join list into CSV

            pr = PR(
                number=data.get("number"),
                author=data.get("user", {}).get("login", data.get("author", "Unknown")),
                created_at=datetime.fromisoformat(
                    data.get("created_at", datetime.now().isoformat()).replace("Z", "+00:00")
                ),
                closed_at=datetime.fromisoformat(
                    data["closed_at"].replace("Z", "+00:00")
                ) if data.get("closed_at") else None,
                state=data.get("state", "open"),
                reviewers=reviewers
            )
            session.merge(pr)
            session.commit()
        finally:
            session.close()

    def get_commits(self, days=7):
        session = self.Session()
        since = datetime.now() - timedelta(days=days)
        commits = session.query(Commit).filter(Commit.date >= since).all()
        session.close()
        return commits

    def get_prs(self, days=7):
        session = self.Session()
        since = datetime.now() - timedelta(days=days)
        prs = session.query(PR).filter(PR.created_at >= since).all()
        session.close()

        # ✅ Add parsed list of reviewers for easier downstream use
        for pr in prs:
            if pr.reviewers:
                pr.reviewers = pr.reviewers.split(",")
            else:
                pr.reviewers = []

        return prs
