# CampusFind

A lost and found web app for campuses. Students can report lost or found items, search reports, get suggested matches, and recover belongings through a verified claim process.

**Demo video:** [docs/demo.mp4](docs/demo.mp4)  
**Project guide (PDF):** [docs/CampusFind_Project_Guide.pdf](docs/CampusFind_Project_Guide.pdf)

## Features

- **Google sign-in** (Supabase Auth). Browsing and searching need no login; reporting and claiming do.
- **Report** a lost or found item with category, location, optional phone number and optional photo.
- **Found / Lost tabs** on the home page, with keyword search.
- **Claim verification:** a finder adds a private question when reporting a found item. A claimant must answer it. The finder reviews the answer and approves or rejects. Contact details of found items stay hidden until a claim is approved.
- **Possible matches:** each item page suggests similar reports of the opposite type, using TF-IDF text similarity (scikit-learn).
- **My reports** page and the ability to **delete** your own reports.
- Photo upload to Supabase Storage.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, vanilla JavaScript |
| Backend | Python, Flask (JSON API) |
| Database / Auth / Storage | Supabase (PostgreSQL, Google OAuth, Storage) |
| Matching | scikit-learn (TF-IDF + cosine similarity) |

## Project Structure

```
campusFind/
├── backend/
│   ├── app.py              # Flask app, CORS, blueprints
│   ├── db.py               # Supabase client, login check (require_user)
│   ├── items.py            # items, upload, delete, my items, matches
│   ├── claims.py           # submit, list, approve/reject claims
│   ├── matching.py         # TF-IDF similarity
│   └── requirements.txt
├── frontend/
│   ├── index.html          # Found / Lost tabs + search
│   ├── report.html         # report an item
│   ├── item.html           # details, claim form, claim review, matches
│   ├── my-reports.html     # items you reported
│   ├── auth.js             # Supabase Google sign-in
│   ├── api.js              # API helpers
│   └── style.css
└── docs/
    ├── CampusFind_Project_Guide.pdf
    └── demo.mp4
```

## Setup

### 1. Supabase

Create a project, then run this in the SQL Editor:

```sql
create table items (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text not null,
  category text not null,
  location text not null,
  type text not null check (type in ('lost','found')),
  contact text not null,
  phone text,
  image_url text,
  verification_question text,
  user_id uuid,
  status text default 'open',
  created_at timestamptz default now()
);

create table claims (
  id uuid primary key default gen_random_uuid(),
  item_id uuid references items(id) on delete cascade,
  claimant_id uuid,
  claimant_name text not null,
  claimant_email text not null,
  message text not null,
  status text default 'pending',
  created_at timestamptz default now()
);
```

Then:
- Storage: create a **public** bucket named `item-images`.
- Authentication → Providers → **Google**: enable it with a Google OAuth client ID and secret (Google Cloud Console → Credentials). Add the callback URL shown by Supabase to the OAuth client's authorized redirect URIs.
- Authentication → URL Configuration: add your frontend address (for example `http://127.0.0.1:8000/**`) to the Redirect URLs.

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
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_secret_key
```

> The secret key must stay on the server. Never commit `.env` or put this key in the frontend.

```bash
python app.py
```

The API runs at `http://127.0.0.1:5000`.

### 3. Frontend

Open `frontend/auth.js` and set your Supabase project URL and **publishable** key (safe for the browser). Then, in a second terminal:

```bash
cd frontend
python -m http.server 8000
```

Open `http://127.0.0.1:8000`.

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/health` | No | Health check |
| GET | `/api/items?search=` | No | List or search items (contact details removed) |
| GET | `/api/items/<id>` | No | One item. Contact shown for lost items, the owner, or an approved claimant |
| POST | `/api/items` | Yes | Report an item |
| POST | `/api/upload` | Yes | Upload a photo |
| DELETE | `/api/items/<id>` | Owner | Delete your report |
| GET | `/api/my/items` | Yes | Your reports |
| GET | `/api/items/<id>/matches` | No | Possible matches |
| POST | `/api/items/<id>/claims` | Yes | Submit a claim |
| GET | `/api/items/<id>/claims` | Owner | Claims on your found item |
| POST | `/api/claims/<id>/approve` or `/reject` | Owner | Decide a claim |

## How verification works

1. A finder reports a found item and writes a private question only the owner could answer.
2. The owner signs in, opens the item, and answers the question.
3. The finder sees the answer on the item page and approves or rejects.
4. On approval the item becomes `claimed` and the claimant can see the finder's contact details.

## Roadmap

- Email notifications for matches and claim decisions
- Category and date filters
- Sentence-embedding matching and photo similarity
- Auto-expiry for old reports

## License

For educational use.
