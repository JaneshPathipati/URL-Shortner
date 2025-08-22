# SwiftLink URL Shortener

A full-stack URL shortener application built with Python and Flask.

## Features

- ✅ URL shortening with custom short codes
- ✅ Redirect to original URLs
- ✅ Click tracking and analytics
- ✅ Statistics dashboard
- ✅ Modern responsive frontend
- ✅ SQLite database storage

## Quick Start

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python run.py
   ```

   Or directly:
   ```bash
   python app.py
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve frontend interface |
| POST | `/api/shorten` | Create short URL |
| GET | `/:shortCode` | Redirect to original URL |
| GET | `/api/stats` | Get statistics |
| GET | `/api/recent` | Get recent URLs |
| GET | `/api/url/:shortCode` | Get URL details |
| GET | `/api/health` | Health check |

## Example Usage

### Create short URL
```bash
curl -X POST http://localhost:3000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"originalUrl": "https://example.com/very-long-url"}'
```

### Get statistics
```bash
curl http://localhost:3000/api/stats
```

### Get recent URLs
```bash
curl http://localhost:3000/api/recent
```

## Database Schema

The application uses SQLite with two tables:

### urls table
- `id` - Primary key
- `short_code` - Unique short code
- `original_url` - Original long URL
- `created_at` - Creation timestamp
- `clicks` - Click count
- `last_accessed` - Last access timestamp

### analytics table
- `id` - Primary key
- `url_id` - Foreign key to urls table
- `ip_address` - Visitor IP address
- `user_agent` - Browser user agent
- `referrer` - Referrer URL
- `accessed_at` - Access timestamp

## Project Structure

```
.
├── app.py          # Main Flask application
├── run.py          # Startup script
├── requirements.txt # Python dependencies
├── index.html      # Frontend interface
├── urls.db         # SQLite database (created automatically)
└── README.md       # This file
```

## Technology Stack

- **Backend**: Python 3.7+ with Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **CORS**: Flask-CORS for cross-origin requests

## Development

To run in development mode:
```bash
python run.py
```

The application will automatically reload on code changes.

## Deployment

### Railway Deployment

This project is ready for deployment on Railway. The following files are configured for Railway:

- `Procfile` - Tells Railway how to start the application
- `requirements.txt` - Lists all Python dependencies
- `railway.json` - Railway configuration file

To deploy on Railway:

1. Push your code to a GitHub repository
2. Connect your GitHub repo to Railway
3. Railway will automatically detect the Python project and deploy it
4. The app will be available at the Railway-provided URL

### Manual Deployment

For other platforms, you can use:

```bash
# Install dependencies
pip install -r requirements.txt

# Start with gunicorn (production)
gunicorn app:app

# Or start with Python (development)
python app.py
```

### Environment Variables

- `PORT` - Port number (automatically set by Railway, defaults to 3000)

## License

MIT License
