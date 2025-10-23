import os
from app import app, db, Job, STAGE_OPTIONS
from datetime import datetime, timedelta
import random

def seed_demo_data():
    """Seed the database with fake job applications for demo purposes"""
    
    # Check if table exists and clear existing data if it does
    try:
        db.session.query(Job).delete()
    except:
        # Table doesn't exist yet, that's fine
        pass
    
    # Sample data for generating realistic job applications
    companies = [
        "TechCorp Solutions", "DataSystems Inc", "CloudNative Labs", "AI Innovations", 
        "SecureNet Systems", "MobileFirst Tech", "DevOps Dynamics", "CodeCraft Studios",
        "ByteSize Startups", "FutureStack Labs", "AgileWorks Inc", "Serverless Co",
        "API Masters", "Database Pros", "Frontend Foundry", "Backend Builders"
    ]
    
    job_titles = [
        "Backend Developer", "Frontend Developer", "Full Stack Engineer", "Data Analyst",
        "DevOps Engineer", "Software Engineer", "Python Developer", "JavaScript Developer",
        "Data Scientist", "Machine Learning Engineer", "Cloud Architect", "Database Administrator"
    ]
    
    locations = [
        "Remote", "New York, NY", "San Francisco, CA", "Austin, TX", 
        "Boston, MA", "Chicago, IL", "Seattle, WA", "Denver, CO"
    ]
    
    salary_ranges = [
        "$80,000 - $100,000", "$90,000 - $120,000", "$100,000 - $130,000", 
        "$110,000 - $140,000", "$120,000 - $150,000", "$130,000 - $160,000"
    ]
    
    job_types = ["Full-time", "Contract", "Internship", "Part-time"]
    
    # Create 20 fake job applications with more realistic date distribution
    for i in range(20):
        # Create a more realistic date distribution:
        # - Higher IDs (newer entries) tend to have more recent dates
        # - But with some randomness for realism
        base_days_ago = (20 - i) * 10  # Higher IDs = fewer days ago
        random_variation = random.randint(-15, 15)  # Some entries logged late/early
        days_ago = max(1, base_days_ago + random_variation)  # Ensure no future dates
        
        app_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Generate random scores
        career_fit = random.randint(1, 5)
        interest = random.randint(1, 5)
        growth = random.randint(1, 5)
        salary = random.randint(1, 5)
        total_score = round((career_fit + interest + growth + salary) / 4, 1)
        
        job = Job(
            company_name=random.choice(companies),
            job_title=random.choice(job_titles),
            location=random.choice(locations),
            salary_range=random.choice(salary_ranges),
            job_type=random.choice(job_types),
            application_date=app_date,
            response_status=random.choice(STAGE_OPTIONS),
            career_fit_now=career_fit,
            interest_level=interest,
            growth_potential=growth,
            salary_fit=salary,
            total_score=total_score,
            notes=f"Demo application #{i+1} - Great potential for growth and learning."
        )
        
        db.session.add(job)
    
    # Commit all the new jobs to the database
    db.session.commit()
    print("Demo database seeded with 20 fake job applications!")

if __name__ == "__main__":
    with app.app_context():
        seed_demo_data()