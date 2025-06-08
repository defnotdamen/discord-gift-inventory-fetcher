## Features

- Supports multiple Discord tokens from `tokens.txt`  
- Automatically claims ExitLag promo codes via Discord API  
- Saves successfully claimed promo codes to `gift_codes.txt`  
- Shows success and error logs with timestamps and color-coded UI in the console  
- Optional proxy support (can be disabled)  
- Thread-safe file writing for safe concurrent access  

## Setup

1. Clone or download this repository.  
2. Create a file named `tokens.txt` with your Discord tokens, one per line.  
   - Format can be either plain token or `email:password:token` (token will be extracted automatically).  
3. (Optional) Create a `proxies.txt` file if you want to use proxies, one proxy per line in format:  
