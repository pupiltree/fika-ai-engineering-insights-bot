from storage.database import Database, PR
from datetime import datetime, timedelta
import random

def insert_dummy_prs():
    db = Database()
    session = db.Session()  # ✅ corrected function name

    authors = ["Alice", "Bob", "Charlie", "David"]
    reviewers_map = {
        "Alice": ["Bob", "Charlie"],
        "Bob": ["Alice", "David"],
        "Charlie": ["David", "Alice"],
        "David": ["Bob", "Charlie"]
    }

    today = datetime.now()
    for i in range(1, 11):
        author = random.choice(authors)
        reviewers = reviewers_map.get(author, [])
        reviewers = random.sample(reviewers, k=random.randint(1, len(reviewers)))

        pr = PR(
            number=i,
            author=author,
            reviewers=",".join(reviewers),
            created_at=(today - timedelta(days=random.randint(10, 29))),
            closed_at=(today - timedelta(days=random.randint(0, 9))),
            state="closed"
        )
        session.merge(pr)

    session.commit()
    print("✅ Inserted dummy PRs into correct table!")

if __name__ == "__main__":
    insert_dummy_prs()
