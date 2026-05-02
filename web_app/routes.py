"""
Flask Routes – handles file uploads, analysis pipeline, and results.
Background processing via threading to avoid HTTP timeouts.
"""

import os
import sys
import uuid
import threading
import traceback

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, jsonify,
)

# Ensure project root is on sys.path so our modules resolve
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from resume_parser import ResumeParser
from web_app.auth import login_required_decorator

main = Blueprint('main', __name__)

# Lightweight modules — safe at import time
parser = ResumeParser()

# In-memory store for analysis data (avoids cookie size limits)
_data_store: dict = {}

# Background job results store
_job_store: dict = {}

# Heavy modules — lazy singletons (loaded on first analysis request)
_nlp_processor = None
_matching_engine = None
_visualizer = None
_explainer = None


def _get_nlp_processor():
    global _nlp_processor
    if _nlp_processor is None:
        from nlp_processing import NLPProcessor
        _nlp_processor = NLPProcessor()
    return _nlp_processor


def _get_matching_engine():
    global _matching_engine
    if _matching_engine is None:
        from matching_engine import MatchingEngine
        _matching_engine = MatchingEngine()
    return _matching_engine


def _get_visualizer():
    global _visualizer
    if _visualizer is None:
        from visualization import Visualizer
        _visualizer = Visualizer()
    return _visualizer


def _get_explainer():
    global _explainer
    if _explainer is None:
        from explainable_ai import Explainer
        _explainer = Explainer()
    return _explainer


ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------------------------------------------------------ #
#  Background Analysis Worker
# ------------------------------------------------------------------ #

def _run_analysis(job_id: str, jd_text: str, resumes: list[dict], weights: dict = None):
    """Run the full NLP + matching pipeline in a background thread."""
    try:
        _job_store[job_id]['status'] = 'loading_models'
        _job_store[job_id]['message'] = 'Loading NLP models...'

        # ----- NLP Processing -----
        nlp = _get_nlp_processor()
        _job_store[job_id]['status'] = 'processing_jd'
        _job_store[job_id]['message'] = 'Analysing job description...'

        jd_nlp = nlp.process(jd_text)

        _job_store[job_id]['status'] = 'processing_resumes'
        _job_store[job_id]['message'] = f'Analysing {len(resumes)} resume(s)...'

        resume_nlp_list = [nlp.process(r['text']) for r in resumes]

        # Merge original text into NLP results (matcher needs r['text'] for TF-IDF)
        for i, r in enumerate(resumes):
            resume_nlp_list[i]['text'] = r['text']

        # ----- Matching (with detailed breakdown) -----
        _job_store[job_id]['status'] = 'computing_scores'
        _job_store[job_id]['message'] = 'Computing match scores with embeddings...'

        score_details = _get_matching_engine().compute_scores_detailed(
            jd_text=jd_text,
            jd_tech_skills=jd_nlp['technical_skills'],
            jd_soft_skills=jd_nlp['soft_skills'],
            resumes=resume_nlp_list,
            jd_yoe=jd_nlp.get('years_of_experience', 0),
            weights=weights
        )

        # ----- Explainability -----
        _job_store[job_id]['status'] = 'generating_explanations'
        _job_store[job_id]['message'] = 'Generating explanations...'

        explainer = _get_explainer()
        explanations = []
        for i, r in enumerate(resumes):
            explanation = explainer.explain(
                candidate_name=r['name'],
                match_score=score_details[i]['final_score'],
                resume_technical_skills=resume_nlp_list[i]['technical_skills'],
                resume_soft_skills=resume_nlp_list[i]['soft_skills'],
                jd_technical_skills=jd_nlp['technical_skills'],
                jd_soft_skills=jd_nlp['soft_skills'],
                score_breakdown=score_details[i],
            )
            explanations.append(explanation)

        # ----- Ranking -----
        explanations.sort(key=lambda e: e['match_score'], reverse=True)

        names = [e['candidate_name'] for e in explanations]
        exp_scores = [e['match_score'] for e in explanations]

        # ----- Visualization -----
        _job_store[job_id]['status'] = 'creating_charts'
        _job_store[job_id]['message'] = 'Creating visualisations...'

        viz = _get_visualizer()
        score_chart = viz.candidate_score_chart(names, exp_scores)
        skill_chart = viz.skill_distribution_chart(explanations)
        soft_chart = viz.soft_skills_chart(explanations)

        # ----- Done -----
        _job_store[job_id].update({
            'status': 'done',
            'message': 'Analysis complete!',
            'results': {
                'explanations': explanations,
                'score_chart': score_chart,
                'skill_chart': skill_chart,
                'soft_chart': soft_chart,
                'jd_skills': jd_nlp['technical_skills'],
                'custom_weights': weights,
            },
        })

    except Exception as e:
        _job_store[job_id].update({
            'status': 'error',
            'message': f'Analysis failed: {str(e)}',
            'error': traceback.format_exc(),
        })


# ------------------------------------------------------------------ #
#  Pages
# ------------------------------------------------------------------ #

@main.route('/')
def home():
    return render_template('home.html')


@main.route('/upload', methods=['GET', 'POST'])
@login_required_decorator
def upload():
    if request.method == 'POST':
        # --- Job Description ---
        jd_text = request.form.get('job_description', '').strip()
        jd_file = request.files.get('jd_file')

        if jd_file and jd_file.filename and allowed_file(jd_file.filename):
            jd_text = parser.parse_bytes(jd_file.read(), jd_file.filename)
        elif not jd_text:
            flash('Please provide a job description (text or file).', 'danger')
            return redirect(url_for('main.upload'))

        # --- Resumes ---
        resume_files = request.files.getlist('resumes')
        if not resume_files or not resume_files[0].filename:
            flash('Please upload at least one resume.', 'danger')
            return redirect(url_for('main.upload'))

        resumes_data: list[dict] = []
        for rf in resume_files:
            if rf and rf.filename and allowed_file(rf.filename):
                raw_text = parser.parse_bytes(rf.read(), rf.filename)
                name = os.path.splitext(rf.filename)[0].replace('_', ' ').replace('-', ' ').title()
                resumes_data.append({'name': name, 'text': raw_text})

        if not resumes_data:
            flash('No valid resume files uploaded.', 'danger')
            return redirect(url_for('main.upload'))

        # --- Custom Weights ---
        try:
            w_tech = float(request.form.get('weight_tech', 60))
            w_yoe = float(request.form.get('weight_yoe', 15))
            w_context = float(request.form.get('weight_context', 15))
            w_soft = float(request.form.get('weight_soft', 10))
            w_bonus = float(request.form.get('weight_bonus', 5))
        except ValueError:
            w_tech, w_yoe, w_context, w_soft, w_bonus = 60.0, 15.0, 15.0, 10.0, 5.0
            
        total_w = w_tech + w_yoe + w_context + w_soft
        if total_w == 0:
            weights = {'tech': 0.60, 'yoe': 0.15, 'context': 0.15, 'soft': 0.10, 'bonus': 0.05}
        else:
            weights = {
                'tech': w_tech / total_w,
                'yoe': w_yoe / total_w,
                'context': w_context / total_w,
                'soft': w_soft / total_w,
                'bonus': w_bonus / 100.0
            }

        # Store data server-side, put only the key in the cookie session
        data_id = str(uuid.uuid4())
        _data_store[data_id] = {
            'jd_text': jd_text,
            'resumes': resumes_data,
            'weights': weights
        }
        session['data_id'] = data_id
        return redirect(url_for('main.analyze'))

    return render_template('upload.html')


@main.route('/analyze')
@login_required_decorator
def analyze():
    data_id = session.get('data_id')
    data = _data_store.get(data_id) if data_id else None

    if not data:
        flash('Please upload job description and resumes first.', 'warning')
        return redirect(url_for('main.upload'))

    jd_text = data['jd_text']
    resumes = data['resumes']
    return render_template('analyze.html',
                           jd_preview=jd_text[:300] + ('...' if len(jd_text) > 300 else ''),
                           num_resumes=len(resumes))


# ------------------------------------------------------------------ #
#  Async Analysis API
# ------------------------------------------------------------------ #

@main.route('/start-analysis', methods=['POST'])
@login_required_decorator
def start_analysis():
    """Kick off background analysis and return a job ID."""
    data_id = session.get('data_id')
    data = _data_store.get(data_id) if data_id else None

    if not data:
        return jsonify({'error': 'No data found. Please upload again.'}), 400

    job_id = str(uuid.uuid4())
    _job_store[job_id] = {
        'status': 'queued',
        'message': 'Starting analysis...',
    }

    # Launch background thread
    thread = threading.Thread(
        target=_run_analysis,
        args=(job_id, data['jd_text'], data['resumes'], data.get('weights')),
        daemon=True,
    )
    thread.start()

    session['job_id'] = job_id
    return jsonify({'job_id': job_id})


@main.route('/analysis-status/<job_id>')
@login_required_decorator
def analysis_status(job_id):
    """Poll endpoint — returns current status of a background analysis job."""
    job = _job_store.get(job_id)
    if not job:
        return jsonify({'status': 'not_found', 'message': 'Job not found'}), 404

    return jsonify({
        'status': job['status'],
        'message': job['message'],
    })


@main.route('/results')
@login_required_decorator
def results():
    """Render the results page for a completed job."""
    job_id = session.get('job_id')
    job = _job_store.get(job_id) if job_id else None

    if not job or job.get('status') != 'done':
        flash('No completed analysis found. Please start over.', 'warning')
        return redirect(url_for('main.upload'))

    r = job['results']

    # Clean up stored data
    data_id = session.get('data_id')
    _data_store.pop(data_id, None)

    return render_template(
        'results.html',
        explanations=r['explanations'],
        score_chart=r['score_chart'],
        skill_chart=r['skill_chart'],
        soft_chart=r['soft_chart'],
        jd_skills=r['jd_skills'],
        custom_weights=r.get('custom_weights'),
    )
