from storage.database import Database, Commit
from datetime import datetime, timedelta
import random

def insert_dummy_commits():
    db = Database()
    session = db.Session()  # Get the session object properly

    authors = ["Alice", "Bob", "Charlie", "David"]
    today = datetime.now()

    for i in range(1, 21):  # Create 20 dummy commits
        commit = Commit(
            sha=f"dummysha{i}",
            author=random.choice(authors),
            date=(today - timedelta(days=random.randint(0, 29))),
            additions=random.randint(10, 200),
            deletions=random.randint(5, 150),
            files_changed=random.randint(1, 5)
        )
        session.merge(commit)  # Merge prevents UNIQUE constraint errors

    session.commit()
    print("✅ Inserted dummy commits into correct table!")

if __name__ == "__main__":
    insert_dummy_commits()
