"""Job Application Tracker — Elijah Sterling | COP4751 Course Project."""
import json
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash
from mysql.connector import Error
from database import query, get_db, json_value

app = Flask(__name__)
app.secret_key = "replace-this-with-a-random-secret-key"

# Form field metadata and SQL identifiers are application constants (not user input).
ENTITIES = {
    "companies": {
        "title": "Companies", "table": "companies", "pk": "company_id",
        "fields": [
            ("company_name", "Company name", "text", True), ("industry", "Industry", "text", False),
            ("website", "Website", "url", False), ("city", "City", "text", False),
            ("state", "State", "text", False), ("notes", "Notes", "textarea", False)],
        "list_sql": "SELECT c.*, (SELECT COUNT(*) FROM jobs j WHERE j.company_id=c.company_id) AS job_count FROM companies c ORDER BY c.company_name",
    },
    "jobs": {
        "title": "Jobs", "table": "jobs", "pk": "job_id",
        "fields": [("company_id", "Company", "company", True), ("job_title", "Job title", "text", True),
            ("job_type", "Job type", "enum_job", True), ("salary_min", "Minimum salary ($)", "number", False),
            ("salary_max", "Maximum salary ($)", "number", False), ("job_url", "Job URL", "url", False),
            ("date_posted", "Date posted", "date", False), ("requirements", "Required skills (JSON array or comma-separated)", "json", False)],
        "list_sql": "SELECT j.*, c.company_name FROM jobs j JOIN companies c ON c.company_id=j.company_id ORDER BY j.job_title",
    },
    "applications": {
        "title": "Applications", "table": "applications", "pk": "application_id",
        "fields": [("job_id", "Job", "job", True), ("application_date", "Application date", "date", True),
            ("status", "Status", "enum_status", True), ("resume_version", "Resume version", "text", False),
            ("cover_letter_sent", "Cover letter sent", "boolean", False),
            ("interview_data", "Interview details (JSON object)", "json_object", False)],
        "list_sql": "SELECT a.*, j.job_title, c.company_name FROM applications a JOIN jobs j ON j.job_id=a.job_id JOIN companies c ON c.company_id=j.company_id ORDER BY a.application_date DESC",
    },
    "contacts": {
        "title": "Contacts", "table": "contacts", "pk": "contact_id",
        "fields": [("company_id", "Company", "company", True), ("contact_name", "Contact name", "text", True),
            ("title", "Title", "text", False), ("email", "Email", "email", False),
            ("phone", "Phone", "tel", False), ("linkedin_url", "LinkedIn URL", "url", False),
            ("notes", "Notes", "textarea", False)],
        "list_sql": "SELECT ct.*, c.company_name FROM contacts ct JOIN companies c ON c.company_id=ct.company_id ORDER BY ct.contact_name",
    },
}
JOB_TYPES = ["Full-time", "Part-time", "Contract", "Internship"]
STATUSES = ["Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"]


def form_options():
    return {"companies": query("SELECT company_id, company_name FROM companies ORDER BY company_name"),
            "jobs": query("SELECT j.job_id, j.job_title, c.company_name FROM jobs j JOIN companies c ON c.company_id=j.company_id ORDER BY j.job_title")}


def normalize_form(entity):
    cfg = ENTITIES[entity]
    data = {}
    for name, label, kind, required in cfg["fields"]:
        value = request.form.get(name, "").strip()
        if required and not value:
            raise ValueError(f"{label} is required.")
        if kind == "number":
            data[name] = int(value) if value else None
            if data[name] is not None and data[name] < 0:
                raise ValueError(f"{label} cannot be negative.")
        elif kind == "boolean":
            data[name] = 1 if request.form.get(name) == "1" else 0
        elif kind in ("json", "json_object"):
            default = "{}" if kind == "json_object" else "[]"
            data[name] = json_value(value, default)
        else:
            data[name] = value or None
    if entity == "jobs" and data.get("salary_min") is not None and data.get("salary_max") is not None and data["salary_min"] > data["salary_max"]:
        raise ValueError("Minimum salary cannot exceed maximum salary.")
    if entity == "applications" and data.get("application_date"):
        try:
            date.fromisoformat(data["application_date"])
        except ValueError:
            raise ValueError("Please enter a valid application date.")
    return data


@app.route("/")
def dashboard():
    stats = {
        "companies": query("SELECT COUNT(*) AS n FROM companies", fetch="one")["n"],
        "jobs": query("SELECT COUNT(*) AS n FROM jobs", fetch="one")["n"],
        "applications": query("SELECT COUNT(*) AS n FROM applications", fetch="one")["n"],
        "interviews": query("SELECT COUNT(*) AS n FROM applications WHERE status='Interview'", fetch="one")["n"],
        "offers": query("SELECT COUNT(*) AS n FROM applications WHERE status='Offer'", fetch="one")["n"],
    }
    recent = query("SELECT a.application_id,a.application_date,a.status,j.job_title,c.company_name FROM applications a JOIN jobs j ON j.job_id=a.job_id JOIN companies c ON c.company_id=j.company_id ORDER BY a.application_date DESC LIMIT 6")
    return render_template("dashboard.html", stats=stats, recent=recent)


@app.route("/<entity>")
def list_entity(entity):
    if entity not in ENTITIES:
        return redirect(url_for("dashboard"))
    cfg = ENTITIES[entity]
    rows = query(cfg["list_sql"])
    return render_template("entity.html", entity=entity, cfg=cfg, rows=rows, options=form_options(), record=None, mode="list", job_types=JOB_TYPES, statuses=STATUSES)


@app.route("/<entity>/new", methods=["GET", "POST"])
def create_entity(entity):
    if entity not in ENTITIES:
        return redirect(url_for("dashboard"))
    cfg = ENTITIES[entity]
    if request.method == "POST":
        try:
            data = normalize_form(entity)
            columns = list(data.keys())
            sql = f"INSERT INTO {cfg['table']} ({', '.join(columns)}) VALUES ({', '.join(['%s']*len(columns))})"
            query(sql, tuple(data.values()), fetch="lastrowid")
            flash(f"{cfg['title'][:-1] if cfg['title'].endswith('s') else cfg['title']} created successfully.", "success")
            return redirect(url_for("list_entity", entity=entity))
        except (ValueError, Error) as exc:
            flash(str(exc), "error")
    return render_template("entity.html", entity=entity, cfg=cfg, rows=[], options=form_options(), record=None, mode="form", job_types=JOB_TYPES, statuses=STATUSES)


@app.route("/<entity>/<int:record_id>/edit", methods=["GET", "POST"])
def edit_entity(entity, record_id):
    if entity not in ENTITIES:
        return redirect(url_for("dashboard"))
    cfg = ENTITIES[entity]
    record = query(f"SELECT * FROM {cfg['table']} WHERE {cfg['pk']}=%s", (record_id,), fetch="one")
    if not record:
        flash("Record not found.", "error")
        return redirect(url_for("list_entity", entity=entity))
    if request.method == "POST":
        try:
            data = normalize_form(entity)
            assignments = ", ".join(f"{column}=%s" for column in data)
            query(f"UPDATE {cfg['table']} SET {assignments} WHERE {cfg['pk']}=%s", tuple(data.values()) + (record_id,), fetch="rowcount")
            flash("Record updated successfully.", "success")
            return redirect(url_for("list_entity", entity=entity))
        except (ValueError, Error) as exc:
            flash(str(exc), "error")
    return render_template("entity.html", entity=entity, cfg=cfg, rows=[], options=form_options(), record=record, mode="form", job_types=JOB_TYPES, statuses=STATUSES)


@app.route("/<entity>/<int:record_id>/delete", methods=["POST"])
def delete_entity(entity, record_id):
    if entity not in ENTITIES:
        return redirect(url_for("dashboard"))
    cfg = ENTITIES[entity]
    try:
        query(f"DELETE FROM {cfg['table']} WHERE {cfg['pk']}=%s", (record_id,), fetch="rowcount")
        flash("Record deleted successfully.", "success")
    except Error as exc:
        flash(f"Could not delete record: {exc}", "error")
    return redirect(url_for("list_entity", entity=entity))


@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    skills_input = request.form.get("skills", "") if request.method == "POST" else ""
    results = []
    user_skills = {s.strip().lower() for s in skills_input.split(",") if s.strip()}
    if request.method == "POST" and user_skills:
        jobs = query("SELECT j.job_id,j.job_title,j.requirements,c.company_name FROM jobs j JOIN companies c ON c.company_id=j.company_id")
        for job in jobs:
            try:
                required = json.loads(job.get("requirements") or "[]")
                if isinstance(required, dict):
                    required = required.get("skills", [])
                required = [str(skill).strip() for skill in required if str(skill).strip()]
            except (TypeError, ValueError):
                required = []
            required_lower = {skill.lower() for skill in required}
            matched = sorted(user_skills & required_lower)
            missing = sorted(required_lower - user_skills)
            percent = round(100 * len(matched) / len(required_lower)) if required_lower else 0
            results.append({**job, "requirements_list": required, "matched": matched, "missing": missing, "percent": percent})
        results.sort(key=lambda item: (-item["percent"], item["job_title"].lower()))
    return render_template("job_match.html", skills_input=skills_input, results=results)


@app.errorhandler(500)
def server_error(error):
    return render_template("error.html", message="A server error occurred. Check your database connection and application logs."), 500


if __name__ == "__main__":
    app.run(debug=True)
