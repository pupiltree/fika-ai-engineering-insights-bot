import matplotlib.pyplot as plt
import io

def generate_weekly_report_chart(data):
    authors = list(data['authors'].keys())
    commits = [data['authors'][a]['commits'] for a in authors]
    fig, ax = plt.subplots()
    ax.bar(authors, commits)
    ax.set_title('Commits per GitHub Username (Weekly)')
    ax.set_ylabel('Commits')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf