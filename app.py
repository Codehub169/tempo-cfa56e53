from flask import Flask, render_template, request, redirect, url_for, g
import database
import click

app = Flask(__name__)

# Database initialization command
@app.cli.command('init-db')
def init_db_command():
    """Clear existing data and create new tables."""
    database.init_db()
    click.echo('Initialized the database.')

@app.route('/', methods=['GET'])
def index():
    """Main dashboard page. Displays workout history and personal records."""
    workouts = database.get_all_workouts_with_exercises()
    personal_records = database.get_all_personal_records()
    return render_template('index.html', workouts=workouts, personal_records=personal_records)

@app.route('/add_workout', methods=['POST'])
def add_workout_route():
    """Handles the submission of the new workout form."""
    try:
        date = request.form.get('date')
        workout_type = request.form.get('workout_type')
        duration_str = request.form.get('duration')

        if not date or not workout_type or not duration_str:
            # Basic validation, could be more sophisticated
            # For now, redirecting back with an error message (not implemented here)
            return redirect(url_for('index')) 

        duration = int(duration_str)

        exercise_names = request.form.getlist('exercise_names')
        exercise_sets_str = request.form.getlist('exercise_sets')
        exercise_reps_str = request.form.getlist('exercise_reps')
        exercise_weights_str = request.form.getlist('exercise_weights')

        exercises_data = []
        for i in range(len(exercise_names)):
            name = exercise_names[i].strip()
            if name: # Only add exercise if name is provided
                try:
                    sets = int(exercise_sets_str[i])
                    reps = int(exercise_reps_str[i])
                    weight = float(exercise_weights_str[i])
                    exercises_data.append({
                        'name': name,
                        'sets': sets,
                        'reps': reps,
                        'weight': weight
                    })
                except (ValueError, IndexError) as e:
                    # Handle cases where conversion fails or lists are mismatched
                    print(f"Skipping exercise due to data error: {e}")
                    # Optionally, add a flash message to inform the user
                    pass # Or raise an error/return specific error page
        
        if not exercises_data and not (date and workout_type and duration > 0):
            # If no valid exercises and workout details are minimal, redirect or error
            print("No valid exercises or workout details provided.")
            return redirect(url_for('index'))

        database.add_workout(date, workout_type, duration, exercises_data)
        # Optionally, add a success flash message here

    except ValueError:
        # Handle error if duration is not a valid integer
        # Optionally, add a flash message here
        print("Invalid duration provided.")
        pass # Fall through to redirect
    except Exception as e:
        print(f"An error occurred while adding workout: {e}")
        # Optionally, add a flash message here
        pass # Fall through to redirect

    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure DB is initialized before first request in debug mode, or use CLI
    # For production, use the CLI command `flask init-db`
    with app.app_context():
         database.init_db() # Ensures DB exists on run if not using CLI first
    app.run(debug=True, host='0.0.0.0', port=9000)
