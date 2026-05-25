"""
Matching Engine – computes a weighted match score based on
explicitly extracted technical vs soft skills, blended with a selectable
context similarity engine.
Returns both final scores AND detailed breakdowns for explainability.
"""

import os
import threading

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from feature_extraction import FeatureExtractor


class MatchingEngine:
    """Compute match scores heavily weighted towards technical skills."""

    MINILM_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    CONTEXT_MODEL_LABELS = {
        "tfidf": "Basic TF-IDF Cosine",
        "minilm": "Advanced MiniLM Semantic",
    }

    def __init__(self, text_weight: float = 0.3, skills_weight: float = 0.7):
        self.text_weight = text_weight
        self.skills_weight = skills_weight
        
        # Within the skills portion, technical skills are worth 80%, soft skills 20%
        self.tech_ratio = 0.8
        self.soft_ratio = 0.2
        
        self.extractor = FeatureExtractor()
        self._minilm_tokenizer = None
        self._minilm_model = None
        self._minilm_lock = threading.Lock()

    def _calculate_skill_score(self, required: list[str], found: list[str]) -> float:
        """Returns percentage (0.0 to 1.0) of required skills that were found."""
        if not required:
            return 1.0  # If none required, they get full points for this section
            
        req_set = {s.lower() for s in required}
        found_set = {s.lower() for s in found}
        
        matched = req_set.intersection(found_set)
        return len(matched) / len(req_set)

    @staticmethod
    def _format_years(value: float | int) -> str:
        """Format years without noisy trailing zeros."""
        value = float(value or 0)
        return str(int(value)) if value.is_integer() else f"{value:.2f}".rstrip("0").rstrip(".")

    def _normalise_context_mode(self, context_mode: str | None) -> str:
        """Return a supported context similarity mode."""
        if not context_mode:
            return "tfidf"

        context_mode = context_mode.lower().strip()
        if context_mode in {"advanced", "semantic", "sentence_bert", "sentence-bert"}:
            return "minilm"
        if context_mode in {"basic", "lexical"}:
            return "tfidf"
        return context_mode if context_mode in self.CONTEXT_MODEL_LABELS else "tfidf"

    def _tfidf_similarities(self, jd_text: str, resumes: list[dict]) -> np.ndarray:
        """Return JD-to-resume cosine similarities using the fast TF-IDF engine."""
        all_docs = [jd_text] + [r['text'] for r in resumes]
        tfidf_matrix = self.extractor.tfidf_vectors(all_docs)
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    def _load_minilm(self):
        """Lazy-load MiniLM once, only when Advanced mode is selected."""
        if self._minilm_tokenizer is not None and self._minilm_model is not None:
            return self._minilm_tokenizer, self._minilm_model

        with self._minilm_lock:
            if self._minilm_tokenizer is not None and self._minilm_model is not None:
                return self._minilm_tokenizer, self._minilm_model

            os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
            from transformers import AutoModel, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(self.MINILM_MODEL_NAME, local_files_only=True)
            model = AutoModel.from_pretrained(self.MINILM_MODEL_NAME, local_files_only=True)
            model.eval()

            self._minilm_tokenizer = tokenizer
            self._minilm_model = model
            return tokenizer, model

    @staticmethod
    def _mean_pooling(model_output, attention_mask):
        """Mean-pool transformer token embeddings while ignoring padding tokens."""
        import torch

        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        summed = torch.sum(token_embeddings * input_mask_expanded, dim=1)
        counts = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)
        return summed / counts

    def _minilm_similarities(self, jd_text: str, resumes: list[dict]) -> np.ndarray:
        """Return JD-to-resume cosine similarities using all-MiniLM-L6-v2 embeddings."""
        import torch
        import torch.nn.functional as functional

        tokenizer, model = self._load_minilm()
        docs = [jd_text] + [r['text'] for r in resumes]
        encoded = tokenizer(
            docs,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )

        with torch.no_grad():
            output = model(**encoded)
            embeddings = self._mean_pooling(output, encoded["attention_mask"])
            embeddings = functional.normalize(embeddings, p=2, dim=1)

        sims = torch.matmul(embeddings[0:1], embeddings[1:].T).squeeze(0)
        return sims.cpu().numpy()

    def _context_similarities(self, jd_text: str, resumes: list[dict], context_mode: str | None):
        """Return context similarities plus metadata for the selected engine."""
        mode = self._normalise_context_mode(context_mode)

        if mode == "minilm":
            try:
                sims = self._minilm_similarities(jd_text, resumes)
                return sims, {
                    "context_model": "minilm",
                    "context_model_label": self.CONTEXT_MODEL_LABELS["minilm"],
                    "context_model_warning": "",
                }
            except Exception as exc:
                sims = self._tfidf_similarities(jd_text, resumes)
                return sims, {
                    "context_model": "tfidf_fallback",
                    "context_model_label": "Basic TF-IDF Cosine (MiniLM fallback)",
                    "context_model_warning": f"MiniLM unavailable, used TF-IDF fallback: {exc}",
                }

        sims = self._tfidf_similarities(jd_text, resumes)
        return sims, {
            "context_model": "tfidf",
            "context_model_label": self.CONTEXT_MODEL_LABELS["tfidf"],
            "context_model_warning": "",
        }

    def compute_scores(
        self,
        jd_text: str,
        jd_tech_skills: list[str],
        jd_soft_skills: list[str],
        resumes: list[dict],
        jd_yoe: float = 0,
        weights: dict = None,
        context_mode: str = "tfidf",
    ) -> list[float]:
        """Return list of match scores (0‑100) for each resume using dynamically weighted sum."""
        if not resumes:
            return []

        if weights is None:
            weights = {'tech': 0.60, 'yoe': 0.15, 'context': 0.15, 'soft': 0.10, 'bonus': 0.05}

        # 1. Context Similarity (Basic TF-IDF or Advanced MiniLM)
        text_sim, _ = self._context_similarities(jd_text, resumes, context_mode)

        # 2. Explicit Skill & Experience Matching (Weighted Sum)
        final_scores = []
        for i, resume in enumerate(resumes):
            tech_score = self._calculate_skill_score(jd_tech_skills, resume['technical_skills'])
            soft_score = self._calculate_skill_score(jd_soft_skills, resume['soft_skills'])
            
            resume_yoe = resume.get('years_of_experience', 0)
            if jd_yoe <= 0:
                yoe_score = 1.0
            else:
                yoe_score = min(resume_yoe / jd_yoe, 1.0)
            
            req_tech_set = {s.lower() for s in jd_tech_skills}
            found_tech_set = {s.lower() for s in resume['technical_skills']}
            req_soft_set = {s.lower() for s in jd_soft_skills}
            found_soft_set = {s.lower() for s in resume['soft_skills']}
            extra_tech = found_tech_set - req_tech_set
            extra_soft = found_soft_set - req_soft_set
            bonus_step = weights.get('bonus', 0.05) / 10.0
            extra_bonus = min((len(extra_tech) + len(extra_soft)) * bonus_step, weights.get('bonus', 0.05))
            
            blended = (
                (tech_score * weights['tech']) +
                (soft_score * weights['soft']) +
                (yoe_score * weights['yoe']) +
                (text_sim[i] * weights['context']) +
                extra_bonus
            )
            
            # Scale to 0-100 and format
            score_100 = min(max(blended * 100, 0.0), 100.0)
            final_scores.append(round(score_100, 2))

        return final_scores

    def compute_scores_detailed(
        self,
        jd_text: str,
        jd_tech_skills: list[str],
        jd_soft_skills: list[str],
        resumes: list[dict],
        jd_yoe: float = 0,
        weights: dict = None,
        context_mode: str = "tfidf",
    ) -> list[dict]:
        """Return detailed score breakdowns including matched, extra missing, and bonuses."""
        if not resumes:
            return []

        if weights is None:
            weights = {'tech': 0.60, 'yoe': 0.15, 'context': 0.15, 'soft': 0.10, 'bonus': 0.05}

        # 1. Context Similarity (Basic TF-IDF or Advanced MiniLM)
        text_sim, context_meta = self._context_similarities(jd_text, resumes, context_mode)

        results = []
        for i, resume in enumerate(resumes):
            # Compute distinct skill sets
            req_tech = {s.lower() for s in jd_tech_skills}
            found_tech = {s.lower() for s in resume['technical_skills']}
            matched_tech = req_tech.intersection(found_tech)
            extra_tech = found_tech - req_tech
            
            req_soft = {s.lower() for s in jd_soft_skills}
            found_soft = {s.lower() for s in resume['soft_skills']}
            matched_soft = req_soft.intersection(found_soft)
            extra_soft = found_soft - req_soft

            # Ratios
            tech_match_ratio = len(matched_tech) / len(req_tech) if req_tech else 1.0
            soft_match_ratio = len(matched_soft) / len(req_soft) if req_soft else 1.0
            
            resume_yoe = resume.get('years_of_experience', 0)
            if jd_yoe <= 0:
                yoe_match_ratio = 1.0
            else:
                yoe_match_ratio = min(resume_yoe / jd_yoe, 1.0)
            
            # --- Dynamic Weighting ---
            tech_contrib = tech_match_ratio * weights['tech']
            yoe_contrib = yoe_match_ratio * weights['yoe']
            text_contrib = text_sim[i] * weights['context']
            soft_contrib = soft_match_ratio * weights['soft']
            
            # Bonus points share one cap across extra technical and soft skills.
            bonus_step = weights.get('bonus', 0.05) / 10.0
            bonus_cap = weights.get('bonus', 0.05)
            extra_tech_bonus = len(extra_tech) * bonus_step
            extra_soft_bonus = len(extra_soft) * bonus_step
            extra_bonus = min(extra_tech_bonus + extra_soft_bonus, bonus_cap)
            if extra_tech_bonus + extra_soft_bonus > bonus_cap and (extra_tech or extra_soft):
                scale = bonus_cap / (extra_tech_bonus + extra_soft_bonus)
                extra_tech_bonus *= scale
                extra_soft_bonus *= scale
            
            blended = tech_contrib + soft_contrib + text_contrib + yoe_contrib + extra_bonus
            final = min(max(blended * 100, 0.0), 100.0)
            
            # Combine skill contribs for the breakdown
            skill_contrib = tech_contrib + soft_contrib
            
            results.append({
                'final_score': round(final, 2),
                'text_similarity': round(text_sim[i] * 100, 1),
                'tech_skill_score': round(tech_match_ratio * 100, 1),
                'soft_skill_score': round(soft_match_ratio * 100, 1),
                'yoe_score': round(yoe_match_ratio * 100, 1),
                'combined_skill_score': round((tech_contrib + soft_contrib) * 100, 1),
                'text_contribution': round(text_contrib * 100, 1),
                'skill_contribution': round(skill_contrib * 100, 1),
                'tech_contribution': round(tech_contrib * 100, 1),
                'soft_contribution': round(soft_contrib * 100, 1),
                'yoe_contribution': round(yoe_contrib * 100, 1),
                'extra_skills_bonus': round(extra_bonus * 100, 1),
                'extra_tech_bonus': round(extra_tech_bonus * 100, 1),
                'extra_soft_bonus': round(extra_soft_bonus * 100, 1),
                'jd_yoe': jd_yoe,
                'resume_yoe': resume_yoe,
                'yoe_match_display': (
                    f"{self._format_years(resume_yoe)}/{self._format_years(jd_yoe)}"
                    if jd_yoe > 0 else f"{self._format_years(resume_yoe)}/N/A"
                ),
                **context_meta,
            })

        return results
