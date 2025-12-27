#this file is to generate the access token for the functioning of the one minute candle.

from kiteconnect import KiteConnect
import webbrowser

API_KEY = "API_KEY"
API_SECRET = "API_SECRET_KEY"

kite = KiteConnect(api_key=API_KEY)

# Step 1: Open login URL
login_url = kite.login_url()
print("Login URL:", login_url)
webbrowser.open(login_url)

# Step 2: Paste request token
request_token = input("Paste request_token here: ").strip()

# Step 3: Generate access token
data = kite.generate_session(request_token, api_secret=API_SECRET)
access_token = data["access_token"]

print("\n✅ ACCESS TOKEN GENERATED:")
print(access_token)
