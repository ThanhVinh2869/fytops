from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, BOT_TOKEN
from app.fytops import FyTops

def main():
    fytops = FyTops(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    fytops.run(BOT_TOKEN)
    
if __name__ == "__main__":
    main()