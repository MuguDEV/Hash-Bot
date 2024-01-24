
import feedparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time


def get_yts_feed():
    rss_url = 'https://yts.mx/rss/0/720p/action/5'
    return feedparser.parse(rss_url)



def create_html_content(entries):
    html_content = """
    <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                }
                .movie {
                    border: 1px solid #ddd;
                    padding: 10px;
                    margin-bottom: 20px;
                    background-color: #fff;
                }
                .title {
                    font-size: 18px;
                    font-weight: bold;
                    color: #333;
                }
                .description {
                    color: #666;
                }
                .imdb-rating {
                    font-weight: bold;
                    color: #ff9900;
                }
                .poster {
                    max-width: 100%;
                    height: auto;
                }
            </style>
        </head>
        <body>
    """

    for entry in entries:
        imdb_rating = entry.description.split('IMDB Rating: ')[1].split('<br />')[0]
        genre = entry.description.split('Genre: ')[1].split('<br />')[0]
        size = entry.description.split('Size: ')[1].split('<br />')[0]
        runtime = entry.description.split('Runtime: ')[1].split('<br />')[0]
        poster = entry.description.split('src="')[0].split('"')[0]
        html_content += f"""
            <div class="movie">
                <div class="title">{entry.title}</div>
                <div class="description">{entry.description}</div>
                <div class="imdb-rating">IMDb Rating: {imdb_rating}</div>
                <div>Genre: {genre}</div>
                <div>Size: {size}</div>
                <div>Runtime: {runtime}</div>
                <img class="poster" src="{poster} Poster">
                <div><a href="{entry.link}">Link</a></div>
                <div>Published Date: {entry.published}</div>
            </div>
        """

    html_content += """
        </body>
    </html>
    """

    return html_content

def send_email(subject, html_body, to_email, smtp_server, smtp_port, sender_email, sender_password):
    try:
        # Create a MIME object
        message = MIMEMultipart('alternative',None,[MIMEText(html_body, "html")])
        message["From"] = sender_email
        message["To"] = to_email
        message["Subject"] = subject

        # Attach HTML body to the email
        
        # Set up the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Login to the email server
            server.ehlo()
            server.starttls()

            server.login(sender_email, sender_password)

            # Send the email
            server.sendmail(sender_email, to_email, message.as_string())

        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

def main():
    to_email = "the.mugunthan@gmail.com"
    smtp_server = "smtp.gmail.com"  # Replace with your SMTP server
    smtp_port = 587  # Replace with your SMTP server port (e.g., 587 for TLS)
    sender_email = "ytsupadates@gmail.com"  # Replace with your email
    sender_password = "vaos xlsk kbkg qdwq"  # Replace with your email password

    last_entries = None

    while True:
        try:
            feed = get_yts_feed()

            # Check if there are updates since the last check
            if last_entries is None or feed.entries != last_entries:
                print("New updates found!")

                # Create HTML content
                html_content = create_html_content(feed.entries)

                # Send email with HTML content
                send_email("YTS RSS Updates", html_content, to_email, smtp_server, smtp_port, sender_email, sender_password)

                # Update last entries
                last_entries = feed.entries

            # Wait for the next check after 1 hour
            time.sleep(3600)

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
