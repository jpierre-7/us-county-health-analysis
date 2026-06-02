from flask import Flask, jsonify
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

engine = create_engine(os.getenv('DATABASE_URL'))

@app.route('/health')
def health():
    return 'API is running'

@app.route('/api/measures')
def get_measures():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT measure_id, measure_name FROM measure"))
        measures = [dict(row._mapping) for row in result]
    return jsonify(measures)

@app.route('/api/states')
def get_states():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT state_name FROM county ORDER BY state_name"))
        states = [dict(row._mapping) for row in result]
    return jsonify(states)

@app.route('/api/measures/<measure_name>/by_state')
def get_measure_by_state(measure_name):
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
    return jsonify([dict(row._mapping) for row in result])

@app.route('/api/measures/<measure_name>/trend')
def get_measure_trend(measure_name):
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
    return jsonify([dict(row._mapping) for row in result])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))