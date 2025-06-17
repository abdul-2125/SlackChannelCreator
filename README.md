# Slack Channel Creator

This application receives Google Forms submissions and creates Slack channels automatically.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.template` to `.env` and fill in your Slack tokens and database URL.
3. Run the application:
   ```bash
   uvicorn main:app
   ```

## Example Request

Send a POST request to `/forms/webhook` with JSON body:
```json
{
  "channel_name": "my-channel",
  "requester_email": "user@example.com",
  "visibility": "public"
}
```
