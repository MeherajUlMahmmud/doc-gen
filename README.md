# Document Generator

A full-stack document generation application with user authentication, signature management, and 2FA support.

## Tech Stack

### Backend
- **Framework**: Django 5.2.8 + Django REST Framework 3.16.1
- **Authentication**: JWT (Simple JWT)
- **Database**: SQLite (development)
- **Document Processing**: python-docx, docx2pdf
- **Task Queue**: Celery + Redis
- **API Documentation**: drf-yasg (Swagger)

### Frontend
- **Framework**: React 19.2.0 + Vite
- **Language**: TypeScript
- **UI Library**: Shadcn UI (Radix UI components)
- **Styling**: Tailwind CSS 4.1.17
- **Routing**: React Router DOM 7.9.6
- **Forms**: React Hook Form + Zod validation
- **HTTP Client**: Axios 1.13.2
- **Notifications**: Sonner

## Features

### Authentication & User Management
- ✅ User registration and login
- ✅ JWT token-based authentication
- ✅ Account locking after 5 failed login attempts (30-minute lockout)
- ✅ Profile management (designation, division)
- ✅ Profile picture upload

### Signature & Security
- ✅ Digital signature upload
- ✅ PIN-based signature protection
- ✅ Two-factor authentication (TOTP)
- ✅ QR code generation for 2FA setup

### Document Management (Coming Soon)
- Template management
- Document generation from templates
- Dynamic field population
- Version control
- Signature workflows

## Project Structure

```
doc-gen/
├── doc-gen-backend/          # Django REST API
│   ├── common/               # Shared utilities
│   │   ├── api_response.py   # Standard API responses
│   │   ├── custom_view.py    # Custom API view classes
│   │   ├── custom_pagination.py
│   │   └── custom_permissions.py
│   ├── user_control/         # User management
│   │   ├── models.py         # User and LoginAttempt models
│   │   ├── serializers/      # User serializers
│   │   ├── views.py          # Authentication & profile APIs
│   │   └── urls.py           # API endpoints
│   └── document_control/     # Document management (existing)
│
└── doc-gen-frontend/         # React SPA
    ├── src/
    │   ├── components/       # Reusable components
    │   │   ├── ui/           # Shadcn UI components (50+)
    │   │   ├── common/       # Shared components
    │   │   ├── auth/         # Auth components
    │   │   └── layout/       # Layout components
    │   ├── pages/            # Page components
    │   │   ├── auth/         # Login, Register
    │   │   └── profile/      # Profile, SignatureSetup
    │   ├── services/         # API services
    │   │   ├── api.ts        # Axios instance
    │   │   ├── auth.ts       # Auth API calls
    │   │   └── users.ts      # User API calls
    │   ├── context/          # React contexts
    │   │   └── AuthContext.tsx
    │   ├── schemas/          # Zod validation schemas
    │   ├── types/            # TypeScript types
    │   └── lib/              # Utilities
    └── public/
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- Redis (for Celery)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd doc-gen-backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

   The API will be available at: `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd doc-gen-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` if needed (default: `VITE_API_URL=http://localhost:8000`)

4. **Run development server**
   ```bash
   npm run dev
   ```

   The app will be available at: `http://localhost:5173`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - Login and get JWT tokens
- `POST /api/v1/auth/logout/` - Logout (blacklist refresh token)

### User Profile
- `GET /api/v1/users/profile/` - Get current user profile
- `PATCH /api/v1/users/profile/update/` - Update designation/division

### Signature & Security
- `PATCH /api/v1/users/signature/upload/` - Upload signature file
- `POST /api/v1/users/pin/setup/` - Setup/change signature PIN
- `GET /api/v1/users/2fa/setup/` - Get 2FA QR code
- `POST /api/v1/users/2fa/setup/` - Enable/disable 2FA

### API Documentation
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## API Response Format

All API responses follow this structure:

```json
{
  "status": "success|error",
  "status_code": 200,
  "message": "Operation successful",
  "data": {},
  "errors": {},
  "meta": {
    "prev_page": null,
    "next_page": null,
    "total_pages": 1,
    "total_records": 10
  }
}
```

## Authentication Flow

1. **Register**: User creates account via `/api/v1/auth/register/`
2. **Login**: User authenticates via `/api/v1/auth/login/`, receives access & refresh tokens
3. **Access Protected Routes**: Include `Authorization: Bearer <access_token>` header
4. **Token Refresh**: Frontend automatically refreshes expired access tokens using refresh token
5. **Logout**: Blacklist refresh token via `/api/v1/auth/logout/`

## Account Security

### Account Locking
- After 5 failed login attempts, the account is locked for 30 minutes
- Lock automatically expires after 30 minutes
- Failed attempts are logged with IP address and user agent

### Signature Security
- **PIN Protection**: Users can set a PIN to protect their signature
- **2FA**: TOTP-based two-factor authentication for additional security
- **File Validation**: Signature files must be images under 5MB

## Frontend Routes

### Public Routes
- `/login` - Login page
- `/register` - Registration page

### Protected Routes (require authentication)
- `/` - Dashboard
- `/profile` - User profile management
- `/documents` - Document list (coming soon)
- `/templates` - Template browser (coming soon)

## Development Tips

### Backend
- Custom API views are in `common/custom_view.py`
- All views use `ApiResponse` helper for consistent responses
- Use `CustomPageNumberPagination` for paginated endpoints
- JWT tokens: Access (7 days), Refresh (28 days)

### Frontend
- Use `useAuth()` hook to access auth state
- API calls automatically include JWT token via interceptor
- Forms use react-hook-form + zod for validation
- All Shadcn UI components are pre-installed in `components/ui/`

## Environment Variables

### Backend (`doc-gen-backend/.env`)
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379
```

### Frontend (`doc-gen-frontend/.env`)
```env
VITE_API_URL=http://localhost:8000
```

## Building for Production

### Backend
```bash
# Collect static files
python manage.py collectstatic

# Use production settings
export DJANGO_SETTINGS_MODULE=doc_gen.settings.production
```

### Frontend
```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License

## Support

For issues and questions, please create an issue in the GitHub repository.
