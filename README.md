task:

Rate-Limited Logging Service
Goal: Build a backend service that accepts logs from clients but rate-limits logs by client ID.
Endpoints:
POST /log -d {"client_id": "<id>", "message": "<msg>"}

Accepts the message and stores it along with a timestamp if the client hasn’t exceeded 5 logs per minute.

Returns 201 if accepted, 429 if rate-limited.

GET /logs/<client_id>

Returns the latest 20 logs from that client.
    
Requirements:
Use a SQL database for persistence.# huma-task
