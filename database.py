import sqlite3
import os

DATABASE_FILE = os.path.join('data', 'fitness_tracker.db')

def _get_db_connection():
    """Establishes a database connection."""
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = _get_db_connection()
    cursor = conn.cursor()

    # Workouts table: Stores workout history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            duration INTEGER NOT NULL -- Duration in minutes
        )
    ''')

    # Exercises table: Stores exercises performed in each workout
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL NOT NULL,
            FOREIGN KEY (workout_id) REFERENCES workouts (id) ON DELETE CASCADE
        )
    ''')

    # Personal records table: Tracks personal bests for exercises
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personal_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_name TEXT NOT NULL,
            metric TEXT NOT NULL, -- e.g., 'max_weight'
            value REAL NOT NULL,
            date_achieved TEXT NOT NULL,
            UNIQUE (exercise_name, metric)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DATABASE_FILE}")

def add_workout(date, workout_type, duration, exercises_data):
    """Adds a new workout and its exercises to the database.
    Also updates personal records based on the exercises.

    Args:
        date (str): Date of the workout (YYYY-MM-DD).
        workout_type (str): Type of workout (e.g., Strength, Cardio).
        duration (int): Duration of the workout in minutes.
        exercises_data (list): A list of dictionaries, where each dictionary contains:
            {'name': str, 'sets': int, 'reps': int, 'weight': float}
    """
    conn = _get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert workout
        cursor.execute('''
            INSERT INTO workouts (date, type, duration)
            VALUES (?, ?, ?)
        ''', (date, workout_type, duration))
        workout_id = cursor.lastrowid

        # Insert exercises and update personal records
        for ex_data in exercises_data:
            if not ex_data.get('name'): # Skip if exercise name is empty
                continue
            cursor.execute('''
                INSERT INTO exercises (workout_id, name, sets, reps, weight)
                VALUES (?, ?, ?, ?, ?)
            ''', (workout_id, ex_data['name'], ex_data['sets'], ex_data['reps'], ex_data['weight']))
            
            # Update personal record for max weight
            # Only consider weight if it's positive
            if ex_data['weight'] is not None and ex_data['weight'] > 0:
                update_personal_record(ex_data['name'], 'max_weight', ex_data['weight'], date, conn)
        
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        conn.close()

def update_personal_record(exercise_name, metric, value, date_achieved, existing_conn=None):
    """Updates or inserts a personal record.
    If a record for the exercise and metric exists, it's updated only if the new value is higher.
    """
    conn = existing_conn or _get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO personal_records (exercise_name, metric, value, date_achieved)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(exercise_name, metric) DO UPDATE SET
                value = CASE WHEN excluded.value > value THEN excluded.value ELSE value END,
                date_achieved = CASE WHEN excluded.value > value THEN excluded.date_achieved ELSE date_achieved END
        ''', (exercise_name, metric, value, date_achieved))
        
        if not existing_conn: # Commit only if we opened a new connection
             conn.commit()
    except sqlite3.Error as e:
        if not existing_conn: conn.rollback()
        print(f"Database error while updating PR: {e}")
        # Not raising here to allow workout logging even if PR update fails in some edge cases
        # Or, could re-raise if PR update is critical path
    finally:
        if not existing_conn: conn.close()

def get_all_workouts_with_exercises():
    """Retrieves all workouts along with their associated exercises."""
    conn = _get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, date, type, duration FROM workouts ORDER BY date DESC, id DESC
    ''')
    workouts_rows = cursor.fetchall()

    workouts = []
    for wr in workouts_rows:
        workout = dict(wr)
        cursor.execute('''
            SELECT name, sets, reps, weight FROM exercises WHERE workout_id = ? ORDER BY id ASC
        ''', (workout['id'],))
        workout['exercises'] = [dict(ex) for ex in cursor.fetchall()]
        workouts.append(workout)
    
    conn.close()
    return workouts

def get_all_personal_records():
    """Retrieves all personal records, ordered by exercise name."""
    conn = _get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT exercise_name, metric, value, date_achieved 
        FROM personal_records 
        ORDER BY exercise_name ASC, metric ASC
    ''')
    personal_records = [dict(pr) for pr in cursor.fetchall()]
    
    conn.close()
    return personal_records

if __name__ == '__main__':
    # Example usage: Initialize DB and add some sample data
    init_db()
    print("Database initialized.")
    # Note: The prompt states tables are already created. 
    # This init_db() will create them if they don't exist, which is robust.
