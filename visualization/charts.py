"""
Visualizer – generates matplotlib charts and returns them as
base‑64 encoded PNG strings for embedding in HTML.
"""

import io
import base64

import matplotlib
matplotlib.use('Agg')  # non‑interactive backend
import matplotlib.pyplot as plt
import numpy as np


class Visualizer:
    """Create recruitment analytics charts."""

    # Color palette
    COLORS = [
        '#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd',
        '#818cf8', '#6d28d9', '#5b21b6', '#7c3aed',
        '#4f46e5', '#4338ca',
    ]

    @classmethod
    def candidate_score_chart(cls, names: list[str], scores: list[float]) -> str:
        """Horizontal bar chart comparing candidate match scores."""
        fig, ax = plt.subplots(figsize=(10, max(4, len(names) * 0.7)))

        sorted_pairs = sorted(zip(scores, names))
        sorted_scores, sorted_names = zip(*sorted_pairs) if sorted_pairs else ([], [])

        colors = [cls._score_color(s) for s in sorted_scores]
        bars = ax.barh(sorted_names, sorted_scores, color=colors, height=0.6, edgecolor='white', linewidth=0.5)

        for bar, score in zip(bars, sorted_scores):
            ax.text(
                bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f'{score:.1f}%', va='center', fontsize=10, fontweight='bold',
                color='#1e293b',
            )

        ax.set_xlim(0, 110)
        ax.set_xlabel('Match Score (%)', fontsize=12, fontweight='bold', color='#334155')
        ax.set_title('Candidate Match Score Comparison', fontsize=14, fontweight='bold',
                      color='#1e293b', pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='y', labelsize=10)
        fig.tight_layout()

        return cls._fig_to_base64(fig)

    @classmethod
    def skill_distribution_chart(cls, explanations: list[dict]) -> str:
        """Grouped bar chart: matched vs missing skills per candidate."""
        names = [e['candidate_name'] for e in explanations]
        matched = [len(e['matched_skills']) for e in explanations]
        missing = [len(e['missing_skills']) for e in explanations]

        x = np.arange(len(names))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, max(4, len(names) * 0.8)))
        ax.bar(x - width / 2, matched, width, label='Matched Skills',
               color='#22c55e', edgecolor='white', linewidth=0.5)
        ax.bar(x + width / 2, missing, width, label='Missing Skills',
               color='#ef4444', edgecolor='white', linewidth=0.5)

        ax.set_xlabel('Candidates', fontsize=12, fontweight='bold', color='#334155')
        ax.set_ylabel('Number of Skills', fontsize=12, fontweight='bold', color='#334155')
        ax.set_title('Skill Distribution by Candidate', fontsize=14,
                      fontweight='bold', color='#1e293b', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=30, ha='right', fontsize=10)
        ax.legend(fontsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.tight_layout()

        return cls._fig_to_base64(fig)

    @classmethod
    def soft_skills_chart(cls, explanations: list[dict]) -> str:
        """Bar chart showing soft skills count per candidate."""
        names = [e['candidate_name'] for e in explanations]
        counts = [len(e['detected_soft_skills']) for e in explanations]

        fig, ax = plt.subplots(figsize=(10, max(4, len(names) * 0.7)))
        colors = [cls.COLORS[i % len(cls.COLORS)] for i in range(len(names))]
        bars = ax.bar(names, counts, color=colors, edgecolor='white', linewidth=0.5)

        for bar, count in zip(bars, counts):
            ax.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                str(count), ha='center', fontsize=11, fontweight='bold',
                color='#1e293b',
            )

        ax.set_xlabel('Candidates', fontsize=12, fontweight='bold', color='#334155')
        ax.set_ylabel('Soft Skills Detected', fontsize=12, fontweight='bold', color='#334155')
        ax.set_title('Soft Skills Distribution', fontsize=14,
                      fontweight='bold', color='#1e293b', pad=15)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=30, ha='right', fontsize=10)
        fig.tight_layout()

        return cls._fig_to_base64(fig)

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _fig_to_base64(fig) -> str:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    @staticmethod
    def _score_color(score: float) -> str:
        if score >= 75:
            return '#22c55e'
        if score >= 50:
            return '#f59e0b'
        return '#ef4444'
