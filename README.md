# CampusFind

A simple lost and found web app for campuses. Students can report lost or found items, search recent reports, and submit claims to get their belongings back.

## Features

- Report a lost or found item with details and an optional photo
- Browse and search recent reports
- View item details
- Submit an ownership claim with identifying details
- Admin-only claim approval via a secret token
- Photo storage with Supabase Storage

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, vanilla JavaScript |
| Backend | Python, Flask (JSON API) |
| Database | Supabase (PostgreSQL) |
| File storage | Supabase Storage |

## Project Structure

```
campusFind/
├── backend/
│   ├── app.py            # Flask app, CORS, blueprints
│   ├── db.py             # Supabase client
│   ├── items.py          # Report, list, search, image upload
│   ├── claims.py         # Submit and approve claims
│   └── requirements.txt
└── frontend/
    ├── index.html        # Browse and search items
    ├── report.html       # Report an item
    ├── item.html         # Item details and claim form
    ├── api.js            # API helper functions
    └── style.css
```

## Setup

### 1. Supabase

1. Create a project at [supabase.com](https://supabase.com).
2. In the SQL Editor, create the tables:

```sql
create table items (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text not null,
  category text not null,
  location text not null,
  type text not null check (type in ('lost','found')),
  contact text not null,
  image_url text,
  status text default 'open',
  created_at timestamptz default now()
);

create table claims (
  id uuid primary key default gen_random_uuid(),
  item_id uuid references items(id) on delete cascade,
  claimant_name text not null,
  claimant_email text not null,
  message text not null,
  status text default 'pending',
  created_at timestamptz default now()
);
```

3. Go to **Storage**, create a **public** bucket named `item-images`.

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS / WSL
pip install -r requirements.txt
```

Create `backend/.env`:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_secret_key
ADMIN_TOKEN=any_secret_string_you_choose
```

> Use the Supabase **secret** (service role) key. It must stay on the server. Never commit `.env` or expose this key in the frontend.

Run the server:

```bash
python app.py
```

The API runs at `http://127.0.0.1:5000`.

### 3. Frontend

In a second terminal:

```bash
cd frontend
python -m http.server 8000
```

Open `http://localhost:8000`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/items?search=` | List or search items |
| GET | `/api/items/<id>` | Get one item |
| POST | `/api/items` | Report an item |
| POST | `/api/upload` | Upload an item photo |
| POST | `/api/items/<id>/claims` | Submit a claim |
| POST | `/api/claims/<id>/approve` | Approve a claim (requires `X-Admin-Token` header) |

Example admin approval:

```bash
curl -X POST http://127.0.0.1:5000/api/claims/<claim_id>/approve \
  -H "X-Admin-Token: your_admin_token"
```

## Roadmap

- User login (Supabase Auth)
- Admin dashboard for reviewing claims
- Filters by type, category, and date
- Automatic matching of lost and found reports
- Email notifications

## License

For educational use.
