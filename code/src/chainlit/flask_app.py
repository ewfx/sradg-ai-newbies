from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database file path
DB_FILE = "mydatabase.db"

@app.route("/", methods=["GET", "POST"])
def ihub_system():
    if request.method == "POST":
        # Handle form submission to update the database
        updates = request.form.to_dict()
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            for row_id, new_balance in updates.items():
                if new_balance.strip():  # Only update non-empty fields
                    cursor.execute(
                        f"""
                        UPDATE General_IHub
                        SET 
                            "IHub Balance" = ?,
                            "Balance Difference" = "GL Balance" - ?,
                            "Match Status" = CASE WHEN "GL Balance" - ? = 0 THEN "Match" ELSE "Match Status" END,
                            "anomaly_detected" = CASE WHEN "GL Balance" - ? = 0 THEN "No" ELSE "anomaly_detected"  END,
                            "category" = CASE WHEN "GL Balance" - ? = 0 THEN NULL ELSE "category" END,
                            "possible_cause" = CASE WHEN "GL Balance" - ? = 0 THEN NULL ELSE "possible_cause" END,
                            "recommended_actions" = CASE WHEN "GL Balance" - ? = 0 THEN NULL ELSE "recommended_actions"  END
                        WHERE rowid = ?
                        """,
                        (new_balance, new_balance, new_balance, new_balance, new_balance, new_balance, new_balance, row_id),
                    )
            conn.commit()
        return redirect(url_for("ihub_system"))

    # Fetch all records from the General_IHub table
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT rowid, "As of Date", Account, AU, "IHub Balance" FROM General_IHub ORDER BY Account, AU , "As of Date" DESC'
        )
        rows = cursor.fetchall()

    # Render the HTML page with the data
    return render_template("IHub_system.html", rows=rows)


if __name__ == "__main__":
    app.run(debug=True)