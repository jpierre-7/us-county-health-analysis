from flask import Flask, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# pool_pre_ping=True tests connections before giving them to callers, detecting dropped/paused connections gracefully
engine = create_engine(
    os.getenv('DATABASE_URL'),
    pool_pre_ping=True,
    pool_recycle=300
)

@app.errorhandler(SQLAlchemyError)
def handle_database_error(error):
    logger.error(f"Database error: {str(error)}")
    return jsonify({
        "error": "Database error",
        "message": "Failed to communicate with database. The database may be paused or unreachable.",
        "details": str(error)
    }), 503

@app.errorhandler(Exception)
def handle_general_exception(error):
    logger.error(f"Unhandled exception: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500

@app.route('/health')
@app.route('/api/health')
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Health check DB failure: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 503

@app.route('/api/measures')
def get_measures():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT measure_id, measure_name FROM measure"))
            measures = [dict(row._mapping) for row in result]
        return jsonify(measures), 200
    except SQLAlchemyError as e:
        return handle_database_error(e)

@app.route('/api/states')
def get_states():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DISTINCT state_name FROM county ORDER BY state_name"))
            states = [dict(row._mapping) for row in result]
        return jsonify(states), 200
    except SQLAlchemyError as e:
        return handle_database_error(e)

@app.route('/api/measures/<measure_name>/by_state')
def get_measure_by_state(measure_name):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                                       SELECT state_name, ROUND(AVG(raw_value)::numeric, 4) AS avg_value
                                       FROM fact_observations fo
                                       JOIN measure m ON fo.measure_id = m.measure_id
                                       JOIN county c ON fo.fipscode = c.fipscode
                                       WHERE m.measure_name = :measure_name
                                       AND fo.raw_value IS NOT NULL
                                       GROUP BY c.state_name
                                       ORDER BY avg_value DESC
                                       """), {'measure_name': measure_name})
            data = [dict(row._mapping) for row in result]
        return jsonify(data), 200
    except SQLAlchemyError as e:
        return handle_database_error(e)

@app.route('/api/measures/<measure_name>/trend')
def get_measure_trend(measure_name):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                                       SELECT year_start, ROUND(AVG(raw_value)::numeric, 4) AS avg_value
                                       FROM fact_observations fo
                                       JOIN measure m ON fo.measure_id = m.measure_id
                                       JOIN county c ON fo.fipscode = c.fipscode
                                       WHERE m.measure_name = :measure_name
                                       AND fo.raw_value IS NOT NULL
                                       GROUP BY year_start
                                       ORDER BY year_start ASC
                                       """), {'measure_name': measure_name})
            data = [dict(row._mapping) for row in result]
        return jsonify(data), 200
    except SQLAlchemyError as e:
        return handle_database_error(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
