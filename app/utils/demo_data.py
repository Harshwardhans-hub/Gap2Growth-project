"""
Demo Data Seeder
Contains department-specific activities for each course
"""

from datetime import datetime, time


DEPARTMENT_ACTIVITIES = {
    "Computer Science": [
        {
            "title": "Python Data Structures Practice",
            "category": "Learning",
            "duration_minutes": 30,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Practice implementing and using lists, dictionaries, sets, and tuples in Python. Complete coding exercises to strengthen your understanding."
        },
        {
            "title": "Algorithm Visualization Study",
            "category": "Learning",
            "duration_minutes": 45,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Study sorting and searching algorithms using interactive visualizations. Understand time complexity and optimize your code."
        },
        {
            "title": "SQL Query Challenge",
            "category": "Skill",
            "duration_minutes": 25,
            "difficulty": "Easy",
            "mode": "Solo",
            "description": "Practice writing SQL queries including SELECT, JOIN, GROUP BY, and subqueries. Perfect for database fundamentals."
        },

        {
            "title": "LeetCode Problem Solving",
            "category": "Skill",
            "duration_minutes": 40,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Solve coding problems to prepare for technical interviews. Focus on arrays, strings, and basic algorithms."
        },
    ],
    "Information Technology": [
        {
            "title": "Network Troubleshooting Basics",
            "category": "Skill",
            "duration_minutes": 30,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Learn to diagnose common network issues using ping, traceroute, and netstat commands. Essential IT support skills."
        },
        {
            "title": "Cloud Services Overview",
            "category": "Learning",
            "duration_minutes": 35,
            "difficulty": "Easy",
            "mode": "Solo",
            "description": "Explore AWS, Azure, and Google Cloud basics. Understand IaaS, PaaS, and SaaS models."
        },
        {
            "title": "Cybersecurity Fundamentals",
            "category": "Learning",
            "duration_minutes": 40,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Learn about common security threats, encryption basics, and best practices for data protection."
        },
        {
            "title": "Linux Command Line Practice",
            "category": "Skill",
            "duration_minutes": 25,
            "difficulty": "Easy",
            "mode": "Solo",
            "description": "Practice essential Linux commands for file management, permissions, and system administration."
        },
        {
            "title": "IT Service Management Concepts",
            "category": "Learning",
            "duration_minutes": 30,
            "difficulty": "Easy",
            "mode": "Solo",
            "description": "Understand ITIL framework basics, incident management, and service desk operations."
        },
    ],
    "Electronics": [
        {
            "title": "Circuit Analysis Practice",
            "category": "Learning",
            "duration_minutes": 35,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Practice analyzing DC and AC circuits. Apply Kirchhoff's laws and Thevenin's theorem."
        },
        {
            "title": "Arduino Programming Basics",
            "category": "Skill",
            "duration_minutes": 40,
            "difficulty": "Easy",
            "mode": "Solo",
            "description": "Learn to program Arduino microcontrollers. Create simple LED and sensor projects."
        },
        {
            "title": "Digital Logic Design Review",
            "category": "Learning",
            "duration_minutes": 30,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Review Boolean algebra, logic gates, and combinational circuit design fundamentals."
        },
        {
            "title": "PCB Design Introduction",
            "category": "Skill",
            "duration_minutes": 45,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Learn basics of PCB design using simulation software. Understand component placement and routing."
        },
        {
            "title": "Oscilloscope Measurement Techniques",
            "category": "Skill",
            "duration_minutes": 25,
            "difficulty": "Easy",
            "mode": "Solo",
            "description": "Practice using oscilloscopes to measure voltage, frequency, and analyze waveforms."
        },
    ],
    "Mechanical Engineering": [

        {
            "title": "Thermodynamics Problem Solving",
            "category": "Learning",
            "duration_minutes": 40,
            "difficulty": "Hard",
            "mode": "Solo",
            "description": "Solve problems involving heat transfer, energy conversion, and thermodynamic cycles."
        },
        {
            "title": "Material Science Fundamentals",
            "category": "Learning",
            "duration_minutes": 30,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Review properties of engineering materials: metals, polymers, ceramics, and composites."
        },
        {
            "title": "Engineering Drawing Standards",
            "category": "Skill",
            "duration_minutes": 35,
            "difficulty": "Easy",
            "mode": "Solo",
            "description": "Practice creating technical drawings with proper dimensions, tolerances, and GD&T symbols."
        },
        {
            "title": "Fluid Mechanics Concepts",
            "category": "Learning",
            "duration_minutes": 35,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Study fluid properties, Bernoulli's equation, and pipe flow calculations."
        },
    ],
    "Data Science": [
        {
            "title": "Pandas Data Manipulation",
            "category": "Skill",
            "duration_minutes": 35,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Practice data cleaning, transformation, and analysis using Pandas library in Python."
        },
        {
            "title": "Data Visualization with Matplotlib",
            "category": "Skill",
            "duration_minutes": 30,
            "difficulty": "Easy",
            "mode": "Solo",
            "description": "Create compelling visualizations: bar charts, scatter plots, histograms, and more."
        },
        {
            "title": "Machine Learning Fundamentals",
            "category": "Learning",
            "duration_minutes": 45,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Understand supervised vs unsupervised learning, model training, and evaluation metrics."
        },
        {
            "title": "SQL for Data Analysis",
            "category": "Skill",
            "duration_minutes": 30,
            "difficulty": "Easy",
            "mode": "Solo",
            "description": "Write SQL queries to extract insights from databases. Practice aggregations and joins."
        },
        {
            "title": "Statistical Analysis Basics",
            "category": "Learning",
            "duration_minutes": 40,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Review descriptive statistics, probability distributions, and hypothesis testing."
        },
    ],
    "Business Administration": [
        {
            "title": "Financial Statement Analysis",
            "category": "Learning",
            "duration_minutes": 35,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Learn to read and interpret balance sheets, income statements, and cash flow statements."
        },
        {
            "title": "Marketing Strategy Basics",
            "category": "Learning",
            "duration_minutes": 30,
            "difficulty": "Easy",
            "mode": "Solo",
            "description": "Understand the 4 Ps of marketing, market segmentation, and competitive analysis."
        },
        {
            "title": "Excel for Business Analytics",
            "category": "Skill",
            "duration_minutes": 40,
            "difficulty": "Medium",
            "mode": "Solo",
            "description": "Master Excel functions, pivot tables, and data visualization for business reporting."
        },
        {
            "title": "Project Management Essentials",
            "category": "Learning",
            "duration_minutes": 30,
            "difficulty": "Easy",
            "mode": "Solo",
            "description": "Learn project planning, scheduling, and resource management using Gantt charts."
        },
    ],
}

# Universal activities (available to all departments)
UNIVERSAL_ACTIVITIES = [
    {
        "title": "5-Minute Desk Stretches",
        "category": "Wellness",
        "duration_minutes": 5,
        "difficulty": "Easy",
        "mode": "Solo",
        "course": None,
        "description": "Quick stretching routine for desk workers. Reduce tension and improve posture."
    },
    {
        "title": "Mindfulness Break",
        "category": "Wellness",
        "duration_minutes": 10,
        "difficulty": "Easy",
        "mode": "Solo",
        "course": None,
        "description": "Brief meditation and breathing exercises to refresh your mind."
    },
    {
        "title": "Eye Rest Exercise (20-20-20)",
        "category": "Wellness",
        "duration_minutes": 5,
        "difficulty": "Easy",
        "mode": "Solo",
        "course": None,
        "description": "Follow the 20-20-20 rule: Every 20 minutes, look at something 20 feet away for 20 seconds."
    },
    {
        "title": "Quick Walk Break",
        "category": "Wellness",
        "duration_minutes": 15,
        "difficulty": "Easy",
        "mode": "Solo",
        "course": None,
        "description": "Take a short walk to refresh your mind and get some light exercise."
    },
    {
        "title": "Typing Speed Practice",
        "category": "Skill",
        "duration_minutes": 15,
        "difficulty": "Easy",
        "mode": "Solo",
        "course": None,
        "description": "Improve your typing speed and accuracy with practice exercises."
    },
]


# Demo timetable entries
DEMO_TIMETABLE = [
    {"day": "Monday", "start_time": "09:00", "end_time": "10:00", "course": "Computer Science", "status": "scheduled"},
    {"day": "Monday", "start_time": "11:00", "end_time": "12:00", "course": "Computer Science", "status": "scheduled"},
    {"day": "Monday", "start_time": "14:00", "end_time": "15:00", "course": "Computer Science", "status": "scheduled"},
    {"day": "Tuesday", "start_time": "10:00", "end_time": "11:00", "course": "Computer Science", "status": "scheduled"},
    {"day": "Tuesday", "start_time": "13:00", "end_time": "14:00", "course": "Computer Science", "status": "cancelled"},
    {"day": "Tuesday", "start_time": "15:00", "end_time": "16:00", "course": "Computer Science", "status": "scheduled"},
    {"day": "Wednesday", "start_time": "09:00", "end_time": "10:00", "course": "Computer Science", "status": "scheduled"},
    {"day": "Wednesday", "start_time": "12:00", "end_time": "13:00", "course": "Computer Science", "status": "scheduled"},
    {"day": "Thursday", "start_time": "09:00", "end_time": "10:30", "course": "Computer Science", "status": "scheduled"},
    {"day": "Thursday", "start_time": "11:30", "end_time": "12:30", "course": "Computer Science", "status": "scheduled"},
    {"day": "Thursday", "start_time": "14:00", "end_time": "15:30", "course": "Computer Science", "status": "scheduled"},
    {"day": "Friday", "start_time": "10:00", "end_time": "11:30", "course": "Computer Science", "status": "scheduled"},
    {"day": "Friday", "start_time": "13:00", "end_time": "14:00", "course": "Computer Science", "status": "scheduled"},
]


DEMO_ACTIVITIES = []
for dept, activities in DEPARTMENT_ACTIVITIES.items():
    for activity in activities:
        DEMO_ACTIVITIES.append({**activity, "course": dept})
DEMO_ACTIVITIES.extend(UNIVERSAL_ACTIVITIES)


DEMO_NOTIFICATIONS = [
    "🕐 Free time detected: 60 minutes gap between classes today!",
    "📚 Recommended: Python Data Structures Practice (30 min)",
    "👥 Study group forming for Algorithm Practice at 2 PM",
    "✅ Great job! You completed 3 activities this week.",
    "🎯 New activity available: LeetCode Problem Solving",
]


DEMO_ACTIVITY_LOGS = [
    {"activity_title": "Python Data Structures Practice", "status": "completed", "duration": 30},
    {"activity_title": "5-Minute Desk Stretches", "status": "completed", "duration": 5},
    {"activity_title": "Git & GitHub Workflow", "status": "completed", "duration": 20},
    {"activity_title": "Mindfulness Break", "status": "in_progress", "duration": 10},
]


def get_demo_timetable():
    """Get demo timetable entries"""
    return DEMO_TIMETABLE


def get_demo_activities():
    """Get all demo activities"""
    return DEMO_ACTIVITIES


def get_demo_activities_by_department(department):
    """Get demo activities for a specific department"""
    dept_activities = DEPARTMENT_ACTIVITIES.get(department, [])
    activities_with_course = [
        {**activity, "course": department} 
        for activity in dept_activities
    ]
    return activities_with_course + UNIVERSAL_ACTIVITIES


def get_all_departments():
    """Get list of all available departments"""
    return list(DEPARTMENT_ACTIVITIES.keys())


def get_demo_notifications():
    """Get demo notifications"""
    return DEMO_NOTIFICATIONS


def get_demo_free_slots():
    """Get simulated free time slots for demo"""
    return [
        {"day": "Monday", "start_time": "10:00", "end_time": "11:00", "duration_minutes": 60, "reason": "timetable_gap", "course": "Computer Science"},
        {"day": "Monday", "start_time": "12:00", "end_time": "14:00", "duration_minutes": 120, "reason": "timetable_gap", "course": "Computer Science"},
        {"day": "Tuesday", "start_time": "13:00", "end_time": "14:00", "duration_minutes": 60, "reason": "class_cancelled", "course": "Computer Science"},
        {"day": "Wednesday", "start_time": "10:00", "end_time": "12:00", "duration_minutes": 120, "reason": "timetable_gap", "course": "Computer Science"},
        {"day": "Thursday", "start_time": "10:30", "end_time": "11:30", "duration_minutes": 60, "reason": "timetable_gap", "course": "Computer Science"},
    ]


def get_demo_stats():
    """Get demo statistics"""
    return {
        "completed": 12,
        "in_progress": 2,
        "total_hours": 6.5,
        "total_minutes": 390,
        "this_week": 5,
        "streak_days": 4
    }


def get_demo_recommendations(duration=30, department=None):
    """Get demo activity recommendations based on duration and department"""
    if department and department in DEPARTMENT_ACTIVITIES:
        activities = get_demo_activities_by_department(department)
    else:
        activities = DEMO_ACTIVITIES
    
    suitable = [a for a in activities if a.get("duration_minutes", 30) <= duration]
    
    scored = []
    for activity in suitable:
        score = 50
        if activity.get("course") == department:
            score += 30
        if activity["category"] == "Learning":
            score += 10
        elif activity["category"] == "Skill":
            score += 15
        
        scored.append({
            **activity,
            "id": f"demo-{activity['title'][:10].lower().replace(' ', '-')}",
            "relevance_score": score
        })
    
    scored.sort(key=lambda x: x["relevance_score"], reverse=True)
    return scored


def is_demo_mode():
    """Check if running in demo mode"""
    import os
    return not os.getenv('SUPABASE_URL') or os.getenv('SUPABASE_URL') == ''
