# app.py - COMPLETE CRUD SYSTEM
import os
import csv
from flask import Flask, render_template, request, redirect, url_for, Response, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database config - works both locally and in production
if 'DATABASE_URL' in os.environ:
	# Production (on Render.com) 
	app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DATABASE_URL'].replace("postgres://", "postgresql://", 1)

else:
	# Local development (on laptop)
	basedir = os.path.abspath(os.path.dirname(__file__))
	app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "jobscore.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SECRET_KEY"] = "demo-secret-key-12345"

db = SQLAlchemy(app)

class Job(db.Model):
    __tablename__ = "applications"
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String)
    job_title = db.Column(db.String)
    location = db.Column(db.String)
    salary_range = db.Column(db.String)
    job_type = db.Column(db.String)
    application_date = db.Column(db.String)
    response_status = db.Column(db.String)
    career_fit_now = db.Column(db.Float)
    interest_level = db.Column(db.Float)
    growth_potential = db.Column(db.Float)
    salary_fit = db.Column(db.Float)
    total_score = db.Column(db.Float)
    notes = db.Column(db.String)

# Predefined options for dropdowns
STAGE_OPTIONS = ['Applied', 'Phone Screen', 'Technical Interview', 'Final Interview', 'Offer', 'Rejected', 'No Response']
SCORE_OPTIONS = [1, 2, 3, 4, 5]

@app.route("/")
def home():
    try:
        # Get filter parameters from URL
        search_query = request.args.get('search', '').strip()
        status_filter = request.args.get('status', 'all')
        score_filter = request.args.get('score', 'all')
        sort_by = request.args.get('sort', 'newest')
        
        # Start with all jobs
        jobs_query = Job.query
        
        # Apply search filter
        if search_query:
            jobs_query = jobs_query.filter(
                (Job.company_name.ilike(f'%{search_query}%')) |
                (Job.job_title.ilike(f'%{search_query}%')) |
                (Job.job_type.ilike(f'%{search_query}%'))
            )
        
        # Apply status filter
        if status_filter != 'all':
            jobs_query = jobs_query.filter(Job.response_status == status_filter)
        
        # Apply score filter
        if score_filter != 'all':
            if score_filter == 'high':
                jobs_query = jobs_query.filter(Job.total_score >= 4.0)
            elif score_filter == 'medium':
                jobs_query = jobs_query.filter(Job.total_score.between(2.5, 3.9))
            elif score_filter == 'low':
                jobs_query = jobs_query.filter(Job.total_score <= 2.4)
        
        # Apply sorting
        if sort_by == 'newest':
            jobs_query = jobs_query.order_by(Job.application_date.desc())
        elif sort_by == 'oldest':
            jobs_query = jobs_query.order_by(Job.application_date.asc())
        elif sort_by == 'highest_score':
            jobs_query = jobs_query.order_by(Job.total_score.desc())
        elif sort_by == 'lowest_score':
            jobs_query = jobs_query.order_by(Job.total_score.asc())
        elif sort_by == 'company':
            jobs_query = jobs_query.order_by(Job.company_name.asc())
        else:
            jobs_query = jobs_query.order_by(Job.application_date.desc())
        
        jobs = jobs_query.all()
        
        # Get unique status values for filter dropdown
        unique_statuses = db.session.query(Job.response_status).distinct().all()
        status_options = [status[0] for status in unique_statuses if status[0]]
        
        return render_template("index.html", 
                             jobs=jobs, 
                             columns=[c.name for c in Job.__table__.columns],
                             stage_options=STAGE_OPTIONS,
                             score_options=SCORE_OPTIONS,
                             search_query=search_query,
                             status_filter=status_filter,
                             score_filter=score_filter,
                             sort_by=sort_by,
                             status_options=status_options,
                             total_jobs=len(jobs))
        
    except Exception as e:
        return f"Error loading data: {str(e)}"

@app.route("/add", methods=["GET", "POST"])
def add_job_form():
    if request.method == "POST":
        try:
            # Get form data
            company_name = request.form['company_name']
            job_title = request.form['job_title']
            location = request.form['location']
            job_type = request.form['job_type']
            application_date = request.form['application_date']
            response_status = request.form['response_status']
            
            # Get scores and convert to float
            career_fit_now = float(request.form['career_fit_now'])
            interest_level = float(request.form['interest_level'])
            growth_potential = float(request.form['growth_potential'])
            salary_fit = float(request.form['salary_fit'])
            
            # Auto-calculate total score using your 30/30/20/20 formula
            total_score = (
                interest_level * 0.3 + 
                growth_potential * 0.3 + 
                career_fit_now * 0.2 + 
                salary_fit * 0.2
            )
            
            notes = request.form['notes']
            
            # ========== DEMO MODIFICATION ==========
            # Show flash message instead of saving to database
            flash(f"Demo: Would have added '{job_title}' at {company_name} to your tracker! In the live version, this would be saved.", "success")
            return redirect(url_for('home'))
            
        except Exception as e:
            return f"Error adding job: {str(e)}"
    
    # If GET request, show the form
    return render_template("add_job.html", 
                         stage_options=STAGE_OPTIONS,
                         score_options=SCORE_OPTIONS)

@app.route("/create-db")
def create_db():
    try:
        db.create_all()
        return "✅ Database created! <a href='/'>Go Home</a>"
    except Exception as e:
        return f"Error creating database: {str(e)}"


@app.route("/dashboard-data")
def dashboard_data_enhanced():  # Changed from dashboard_data
    try:
        days_filter = request.args.get('days', 'all')
        jobs = Job.query.all()
        
        # Filter by date if needed
        if days_filter != 'all':
            try:
                from datetime import datetime, timedelta
                filter_days = int(days_filter)
                cutoff_date = datetime.now() - timedelta(days=filter_days)
                
                filtered_jobs = []
                for job in jobs:
                    if job.application_date:
                        app_date = datetime.strptime(job.application_date, '%Y-%m-%d')
                        if app_date >= cutoff_date:
                            filtered_jobs.append(job)
                jobs = filtered_jobs
            except ValueError:
                pass  # If date parsing fails, use all jobs
        
        # Modular data preparation
                # Modular data preparation
        chart_data = {
            'filters': {
                'total_applications': len(jobs),
                'days_filter': days_filter,
                'date_range': f"Last {days_filter} days" if days_filter != 'all' else "All time"
            },
            'charts': {
                'score_distribution': get_score_distribution(jobs),
                'scatter_analysis': get_scatter_analysis(jobs),
                'industry_analysis': get_industry_analysis(jobs),
                'application_trends': get_application_trends(jobs),
                'success_patterns': get_success_patterns(jobs),
                'salary_analysis': get_salary_analysis(jobs),
                'location_analysis': get_location_analysis(jobs),
                'growth_vs_interest': get_growth_vs_interest(jobs),
                'industry_averages': get_industry_averages(jobs),
                'status_analysis': get_status_analysis(jobs),
                'interest_distribution': get_interest_distribution(jobs)
            }
        }
        
        return chart_data
        
    except Exception as e:
        return {'error': str(e)}

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

def get_location_analysis(jobs):
    location_counts = {}
    for job in jobs:
        if job.location:
            # Clean up location data
            location = job.location.strip()
            if location:
                location_counts[location] = location_counts.get(location, 0) + 1
    return dict(sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:8])

def get_salary_analysis(jobs):
    salary_data = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
    for job in jobs:
        if job.salary_fit:
            score = int(job.salary_fit)
            if 1 <= score <= 5:
                salary_data[str(score)] += 1
    return salary_data

def get_growth_vs_interest(jobs):
    scatter_data = []
    for job in jobs:
        scatter_data.append({
            'x': job.interest_level,
            'y': job.growth_potential,
            'company': job.company_name,
            'title': job.job_title,
            'salary_fit': job.salary_fit,
            'total_score': job.total_score
        })
    return scatter_data

def get_industry_averages(jobs):
    """Calculate average scores per industry"""
    industry_data = {}
    
    for job in jobs:
        if job.job_type:
            industries = [tag.strip() for tag in job.job_type.split(',')]
            for industry in industries:
                if industry:
                    if industry not in industry_data:
                        industry_data[industry] = {
                            'count': 0,
                            'total_interest': 0,
                            'total_career_fit': 0, 
                            'total_growth': 0,
                            'total_salary': 0,
                            'total_overall': 0
                        }
                    
                    industry_data[industry]['count'] += 1
                    industry_data[industry]['total_interest'] += job.interest_level
                    industry_data[industry]['total_career_fit'] += job.career_fit_now
                    industry_data[industry]['total_growth'] += job.growth_potential
                    industry_data[industry]['total_salary'] += job.salary_fit
                    industry_data[industry]['total_overall'] += job.total_score
    
    # Convert to averages
    result = {}
    for industry, data in industry_data.items():
        if data['count'] > 0:  # Avoid division by zero
            result[industry] = {
                'avg_interest': data['total_interest'] / data['count'],
                'avg_career_fit': data['total_career_fit'] / data['count'],
                'avg_growth': data['total_growth'] / data['count'],
                'avg_salary': data['total_salary'] / data['count'],
                'avg_overall': data['total_overall'] / data['count'],
                'count': data['count']
            }
    
    return result

# Modular chart data functions - easy to add new ones!
def get_score_distribution(jobs):
    distribution = {'1-2': 0, '2-3': 0, '3-4': 0, '4-5': 0}
    for job in jobs:
        if job.total_score <= 2:
            distribution['1-2'] += 1
        elif job.total_score <= 3:
            distribution['2-3'] += 1
        elif job.total_score <= 4:
            distribution['3-4'] += 1
        else:
            distribution['4-5'] += 1
    return distribution

def get_scatter_analysis(jobs):
    scatter_data = []
    for job in jobs:
        scatter_data.append({
            'x': job.interest_level,
            'y': job.career_fit_now,
            'company': job.company_name,
            'title': job.job_title,
            'total_score': job.total_score,
            'growth': job.growth_potential
        })
    return scatter_data

def get_status_analysis(jobs):
    """Calculate average scores for each application status"""
    status_data = {}
    
    for job in jobs:
        status = job.response_status or 'Applied'  # Default to 'Applied' if empty
        
        if status not in status_data:
            status_data[status] = {
                'count': 0,
                'total_interest': 0,
                'total_career_fit': 0,
                'total_growth': 0,
                'total_salary': 0,
                'total_overall': 0
            }
        
        status_data[status]['count'] += 1
        status_data[status]['total_interest'] += job.interest_level
        status_data[status]['total_career_fit'] += job.career_fit_now
        status_data[status]['total_growth'] += job.growth_potential
        status_data[status]['total_salary'] += job.salary_fit
        status_data[status]['total_overall'] += job.total_score
    
    # Convert to averages
    result = {}
    for status, data in status_data.items():
        if data['count'] > 0:
            result[status] = {
                'avg_interest': round(data['total_interest'] / data['count'], 1),
                'avg_career_fit': round(data['total_career_fit'] / data['count'], 1),
                'avg_growth': round(data['total_growth'] / data['count'], 1),
                'avg_salary': round(data['total_salary'] / data['count'], 1),
                'avg_overall': round(data['total_overall'] / data['count'], 1),
                'count': data['count']
            }
    
    return result

def get_interest_distribution(jobs):
    """Count applications by interest level"""
    interest_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    for job in jobs:
        interest_level = int(job.interest_level)
        if 1 <= interest_level <= 5:
            interest_counts[interest_level] += 1
    
    return interest_counts

def get_industry_analysis(jobs):
    industry_counts = {}
    for job in jobs:
        if job.job_type:
            industries = [tag.strip() for tag in job.job_type.split(',')]
            for industry in industries:
                if industry:
                    industry_counts[industry] = industry_counts.get(industry, 0) + 1
    return dict(sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:10])

def get_application_trends(jobs):
    # Group applications by week
    from collections import defaultdict
    from datetime import datetime
    weekly_trends = defaultdict(int)
    
    for job in jobs:
        if job.application_date:
            try:
                app_date = datetime.strptime(job.application_date, '%Y-%m-%d')
                week_key = app_date.strftime('%Y-%U')  # Year-Week number
                weekly_trends[week_key] += 1
            except ValueError:
                continue
    
    # Convert to sorted list for charting
    trends_data = [{'week': week, 'count': count} 
                  for week, count in sorted(weekly_trends.items())]
    return trends_data

def get_success_patterns(jobs):
    # Analyze what makes high-scoring jobs different
    high_score_jobs = [j for j in jobs if j.total_score >= 4]
    low_score_jobs = [j for j in jobs if j.total_score <= 2]
    
    return {
        'high_score_avg_interest': sum(j.interest_level for j in high_score_jobs) / len(high_score_jobs) if high_score_jobs else 0,
        'high_score_avg_growth': sum(j.growth_potential for j in high_score_jobs) / len(high_score_jobs) if high_score_jobs else 0,
        'low_score_avg_interest': sum(j.interest_level for j in low_score_jobs) / len(low_score_jobs) if low_score_jobs else 0,
        'low_score_avg_growth': sum(j.growth_potential for j in low_score_jobs) / len(low_score_jobs) if low_score_jobs else 0,
        'high_score_count': len(high_score_jobs),
        'low_score_count': len(low_score_jobs)
    }

@app.route("/edit/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):
    job = Job.query.get(job_id)
    
    if not job:
        return "Job not found", 404
    
    if request.method == "POST":
        try:
            # Get form data (keep all validation logic)
            company_name = request.form['company_name']
            job_title = request.form['job_title']
            location = request.form['location']
            job_type = request.form['job_type']
            application_date = request.form['application_date']
            response_status = request.form['response_status']
            
            # Update scores
            career_fit_now = float(request.form['career_fit_now'])
            interest_level = float(request.form['interest_level'])
            growth_potential = float(request.form['growth_potential'])
            salary_fit = float(request.form['salary_fit'])
            
            # Recalculate total score
            total_score = (
                interest_level * 0.3 + 
                growth_potential * 0.3 + 
                career_fit_now * 0.2 + 
                salary_fit * 0.2
            )
            
            notes = request.form['notes']
            
            # ========== DEMO MODIFICATION ==========
            # Show flash message instead of saving to database
            flash(f"Demo: Would have updated '{job_title}' at {company_name}! In the live version, your changes would be saved.", "success")
            return redirect(url_for('home'))
            
        except Exception as e:
            return f"Error updating job: {str(e)}"
    
    # If GET request, show pre-filled form (unchanged)
    return render_template("edit_job.html", 
                         job=job,
                         stage_options=STAGE_OPTIONS,
                         score_options=SCORE_OPTIONS)

@app.route("/import-csv-correct")
def import_csv_correct():
    try:
        csv_file = "jobs.csv"
        
        if not os.path.exists(csv_file):
            return f"❌ CSV file '{csv_file}' not found"
        
        Job.query.delete()
        
        imported_count = 0
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                job = Job(
                    company_name=row.get('company_name', ''),
                    job_title=row.get('position', ''),
                    location=row.get('location', ''),
                    salary_range=f"Score: {row.get('salary_fit', '')}",
                    job_type=row.get('tags', ''),
                    application_date=row.get('date_applied', ''),
                    response_status=row.get('stage', ''),
                    career_fit_now=float(row.get('career_fit_now', 0) or 0),
                    interest_level=float(row.get('interest_level', 0) or 0),
                    growth_potential=float(row.get('growth_potential', 0) or 0),
                    salary_fit=float(row.get('salary_fit', 0) or 0),
                    total_score=float(row.get('total_score', 0) or 0),
                    notes=row.get('notes', '')
                )
                db.session.add(job)
                imported_count += 1
        
        db.session.commit()
        return f"✅ Imported {imported_count} jobs! <a href='/'>View them</a>"
        
    except Exception as e:
        db.session.rollback()
        return f"Error importing CSV: {str(e)}"

@app.route("/delete/<int:job_id>")
def delete_job(job_id):
    try:
        job = Job.query.get(job_id)
        if job:
            # ========== DEMO MODIFICATION ==========
            # Show flash message instead of deleting from database
            flash(f"Demo: Would have deleted '{job.job_title}' at {job.company_name}! In the live version, this would be permanently removed.", "success")
            return redirect(url_for('home'))
        else:
            return "Job not found", 404
    except Exception as e:
        return f"Error deleting job: {str(e)}"

@app.route("/dashboard-test")
def dashboard_test():
    try:
        jobs = Job.query.all()
        return {
            'message': 'Database connection working',
            'total_jobs': len(jobs),
            'sample_job': {
                'company': jobs[0].company_name if jobs else 'No jobs',
                'score': jobs[0].total_score if jobs else 0
            } if jobs else 'No jobs found'
        }
    except Exception as e:
        return {'error': str(e)}

@app.route("/debug-dashboard")
def debug_dashboard():
    try:
        jobs = Job.query.all()
        return {
            'total_jobs': len(jobs),
            'sample_jobs': [
                {
                    'id': job.id,
                    'company': job.company_name,
                    'date': job.application_date,
                    'score': job.total_score
                } for job in jobs[:3]  # First 3 jobs
            ],
            'status': 'Database connection successful'
        }
    except Exception as e:
        return {'error': str(e)}

@app.route("/export-jobs")
def export_jobs():
    try:
        # Get all jobs (you can add filters later if needed)
        jobs = Job.query.all()
        
        # Create CSV content
        output = []
        # CSV header row
        output.append("Company,Job Title,Location,Industry,Application Date,Status,Interest Level,Career Fit,Growth Potential,Salary Fit,Total Score,Notes")
        
        # Add each job as a row
        for job in jobs:
            # Clean data for CSV (handle commas, quotes, etc.)
            company = f'"{job.company_name}"' if ',' in job.company_name else job.company_name
            title = f'"{job.job_title}"' if ',' in job.job_title else job.job_title
            notes = f'"{job.notes}"' if job.notes and ',' in job.notes else (job.notes or "")
            
            row = [
                company,
                title,
                job.location or "",
                job.job_type or "",
                job.application_date or "",
                job.response_status or "",
                str(job.interest_level),
                str(job.career_fit_now),
                str(job.growth_potential),
                str(job.salary_fit),
                str(job.total_score),
                notes
            ]
            output.append(",".join(row))
        
        # Create the response
        response = "\n".join(output)
        return Response(
            response,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=job_applications.csv"}
        )
        
    except Exception as e:
        return f"Error exporting data: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
