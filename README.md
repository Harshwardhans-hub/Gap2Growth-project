# 🎯 Gap2Growth - Adaptive Student Time Utilisation Platform

**Gap2Growth** is an intelligent platform that transforms student downtime into productive learning opportunities. The system automatically detects schedule gaps and class cancellations, then recommends personalized activities to maximize academic growth.

---

## ✨ Features

### For Students
- 📅 **Automatic Free Time Detection** - Real-time identification of schedule gaps and cancelled classes
- 💡 **Smart Recommendations** - Personalized activity suggestions based on available time and learning history
- 📊 **Progress Tracking** - Monitor completed activities, productive hours, and daily streaks
- 🔔 **Instant Notifications** - Get alerted about free time opportunities via in-app and email notifications
- 📈 **Weekly Reports** - Receive engagement summaries and productivity insights

### For Teachers
- 🗓️ **Timetable Management** - Create, edit, and cancel class schedules with visual weekly overview
- 📚 **Activity Creation** - Design learning activities with categories, difficulty levels, and durations
- 👥 **Student Monitoring** - View enrolled students and their engagement statistics
- ⚡ **Instant Notifications** - Students automatically notified when classes are cancelled

### For Administrators
- 👤 **User Management** - Create and manage student/teacher accounts
- 📊 **System Analytics** - View platform-wide engagement statistics
- 📄 **Report Generation** - Generate PDF engagement reports
- 🔧 **System Monitoring** - Monitor database, scheduler, and email service status

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Supabase account (for PostgreSQL database)
- Firebase project (for authentication)
- Gmail account with App Password (for notifications)

### Installation

1. **Clone the repository**
   ```bash
   cd gaptogrowth_demo1
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Copy `.env.example` to `.env` and fill in your credentials:
   ```env
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=development
   FLASK_DEBUG=true
   
   # Database (Supabase)
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   
   # Firebase Authentication
   FIREBASE_CREDENTIALS=firebase-credentials.json
   FIREBASE_API_KEY=your-firebase-api-key
   FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   FIREBASE_PROJECT_ID=your-project-id
   
   # Email Notifications (Gmail)
   GMAIL_EMAIL=your-email@gmail.com
   GMAIL_APP_PASSWORD=your-app-password
   
   # Application URL (change for production)
   APP_URL=http://localhost:5000
   ```

5. **Set up Firebase credentials**
   - Download your Firebase Admin SDK JSON file
   - Save it as `firebase-credentials.json` in the project root

6. **Run the application**
   ```bash
   python app.py
   ```
   
   The application will be available at `http://localhost:5000`

---

## 📁 Project Structure

```
gaptogrowth_demo1/
├── app/
│   ├── routes/           # Flask blueprints
│   │   ├── auth.py       # Authentication routes
│   │   ├── admin.py      # Admin dashboard routes
│   │   ├── teacher.py    # Teacher functionality
│   │   ├── student.py    # Student dashboard routes
│   │   └── api.py        # JSON API endpoints
│   ├── services/         # Business logic
│   │   ├── downtime_service.py      # Free time detection
│   │   ├── recommendation_service.py # Activity recommendations
│   │   ├── notification_service.py   # Notification handling
│   │   ├── realtime_service.py      # Real-time detection engine
│   │   └── report_service.py        # Report generation
│   ├── utils/            # Helper modules
│   │   ├── database.py   # Supabase database operations
│   │   ├── firebase_auth.py # Firebase authentication
│   │   ├── email_sender.py  # Email notifications
│   │   ├── scheduler.py     # Background job scheduler
│   │   ├── decorators.py    # Access control decorators
│   │   └── demo_data.py     # Demo data for testing
│   ├── templates/        # Jinja2 HTML templates
│   │   ├── admin/        # Admin dashboard pages
│   │   ├── auth/         # Login/registration pages
│   │   ├── student/      # Student dashboard pages
│   │   ├── teacher/      # Teacher dashboard pages
│   │   └── base.html     # Base template with sidebar
│   └── static/           # CSS and JavaScript assets
├── app.py               # Application entry point
├── config.py            # Configuration classes
├── wsgi.py              # Production WSGI entry
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables
```

---

## 🔐 Default Login Credentials

### Admin Account
- **Email:** admin@gmail.com
- **Password:** Set via Firebase

### Test Users
Create accounts using the login page with:
- Google Sign-In (for students/teachers)
- Email/Password authentication

---

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase anonymous key | Yes |
| `FIREBASE_CREDENTIALS` | Path to Firebase Admin SDK JSON | Yes |
| `FIREBASE_API_KEY` | Firebase Web API key | Yes |
| `GMAIL_EMAIL` | Gmail address for notifications | For emails |
| `GMAIL_APP_PASSWORD` | Gmail App Password | For emails |
| `APP_URL` | Application base URL | Yes |
| `DOWNTIME_THRESHOLD_MINUTES` | Minimum gap for free time (default: 30) | No |
| `SCHEDULER_ENABLED` | Enable background scheduler | No |

---

## 📡 API Endpoints

### Health Check
- `GET /api/health` - Check system status

### User Information
- `GET /api/me` - Get current user info

### Activities
- `GET /api/activities` - Get all activities
- `GET /api/recommendations?duration=30` - Get activity recommendations

### Timetable
- `GET /api/timetable` - Get user's timetable
- `GET /api/free-slots` - Get detected free time slots

### Notifications
- `GET /api/notifications` - Get user notifications
- `POST /api/notifications/<id>/read` - Mark notification as read

---

## 🚀 Deployment

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

### Environment Setup
1. Set `FLASK_ENV=production`
2. Set `FLASK_DEBUG=false`
3. Update `APP_URL` to your production domain
4. Use a strong `SECRET_KEY`

---

## 📊 Database Schema (Supabase)

The system uses the following tables:
- `users` - User accounts with roles (admin/teacher/student)
- `timetable` - Class schedules with status tracking
- `activities` - Learning activities catalog
- `activity_logs` - Student activity completion records
- `notifications` - User notifications

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---



## 🙏 Acknowledgments

- **Flask** - Web framework
- **Supabase** - Database and backend services  
- **Firebase** - Authentication
- **APScheduler** - Background task scheduling
- **Bootstrap Icons** - UI icons


