"""
Legal-BERT clause classification module for Phase 4 NLP pipeline.
Classifies clauses into 12 risk categories using mock transformer.
"""

import json
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from contract_types import Clause, RiskCategory, ClassificationResult, SeverityLevel


@dataclass
class ClassifierMetrics:
    """Metrics for classifier evaluation."""
    accuracy: float = 0.0
    macro_f1: float = 0.0
    weighted_f1: float = 0.0
    per_category_metrics: Dict[RiskCategory, Dict[str, float]] = field(default_factory=dict)


class LegalBertClassifier:
    """Mock Legal-BERT classifier for clause risk categorization."""
    
    def __init__(self, model_name: str = "legal-bert-base"):
        """Initialize mock classifier."""
        self.model_name = model_name
        self.categories = list(RiskCategory)
        self._init_keyword_mappings()
        self.predictions_cache = {}
    
    def _init_keyword_mappings(self):
        """Initialize keyword mappings for each category."""
        self.category_keywords = {
            RiskCategory.FORCE_MAJEURE: [
                'force majeure', 'unforeseeable', 'act of god', 'extraordinary circumstances',
                'pandemic', 'war', 'natural disaster', 'government action'
            ],
            RiskCategory.TERMINATION: [
                'termination', 'terminate', 'early exit', 'cancellation', 'wind-down',
                'end agreement', 'discontinue', 'close-out'
            ],
            RiskCategory.COVENANTS: [
                'covenant', 'obligation', 'requirement', 'commitment', 'shall', 'must',
                'required to', 'agree to', 'undertake'
            ],
            RiskCategory.FINANCIAL: [
                'financial', 'payment', 'loan', 'debt', 'interest', 'principal', 'cashflow',
                'revenue', 'expense', 'budget', 'cost', 'dscr', 'leverage ratio'
            ],
            RiskCategory.ENVIRONMENTAL: [
                'environmental', 'environmental liability', 'pollution', 'emissions',
                'climate', 'sustainability', 'remediation', 'hazardous', 'carbon'
            ],
            RiskCategory.LABOR: [
                'labor', 'employment', 'worker', 'union', 'strike', 'industrial action',
                'workforce', 'human resource', 'personnel'
            ],
            RiskCategory.SAFETY: [
                'safety', 'hazard', 'health', 'injury', 'accident', 'incident', 'osha',
                'occupational', 'risk management'
            ],
            RiskCategory.INTELLECTUAL_PROPERTY: [
                'intellectual property', 'patent', 'trademark', 'copyright', 'confidentiality',
                'proprietary', 'trade secret', 'confidential information'
            ],
            RiskCategory.DISPUTES: [
                'dispute', 'dispute resolution', 'arbitration', 'litigation', 'claim',
                'controversy', 'disagreement', 'legal action'
            ],
            RiskCategory.INSURANCE: [
                'insurance', 'coverage', 'insure', 'premium', 'claim', 'indemnity',
                'indemnification', 'liable', 'liability'
            ],
            RiskCategory.PENALTIES: [
                'penalty', 'fine', 'liquidated damages', 'payment default', 'breach',
                'remedies', 'damages', 'compensation'
            ],
            RiskCategory.OTHER: [
                'general', 'miscellaneous', 'additional', 'other'
            ]
        }
    
    def classify_clause(self, clause: Clause) -> ClassificationResult:
        """Classify a single clause into risk category."""
        clause_id = clause.clause_id
        
        if clause_id in self.predictions_cache:
            return self.predictions_cache[clause_id]
        
        # Combine title and text for classification
        text_to_classify = (clause.title + " " + clause.text[:500]).lower()
        
        # Score each category
        category_scores = {}
        for category in self.categories:
            score = self._score_category(text_to_classify, category)
            category_scores[category] = score
        
        # Get top predictions
        sorted_scores = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        predicted_category = sorted_scores[0][0]
        confidence = sorted_scores[0][1]
        
        # Normalize confidence to 0-1 range
        confidence = min(1.0, confidence / 10.0)
        
        # Get top-k predictions
        top_k_predictions = [(cat, min(1.0, score / 10.0)) for cat, score in sorted_scores[:5]]
        
        result = ClassificationResult(
            clause_id=clause_id,
            predicted_category=predicted_category,
            confidence=confidence,
            top_k_predictions=top_k_predictions,
            explanation=self._generate_explanation(text_to_classify, predicted_category)
        )
        
        self.predictions_cache[clause_id] = result
        return result
    
    def _score_category(self, text: str, category: RiskCategory) -> float:
        """Score text against a category using keyword matching."""
        keywords = self.category_keywords[category]
        score = 0.0
        
        for keyword in keywords:
            if keyword in text:
                # Count occurrences
                occurrences = text.count(keyword)
                score += 2.0 * occurrences
        
        # Add randomness for realism
        score += random.uniform(-1.0, 1.0)
        
        return max(0.0, score)
    
    def _generate_explanation(self, text: str, category: RiskCategory) -> str:
        """Generate explanation for classification."""
        keywords = self.category_keywords[category]
        found_keywords = [kw for kw in keywords if kw in text]
        
        if found_keywords:
            return f"Detected keywords: {', '.join(found_keywords[:3])}"
        return f"Classified as {category.value} based on semantic analysis"
    
    def classify_clauses(self, clauses: List[Clause]) -> List[ClassificationResult]:
        """Classify multiple clauses."""
        results = []
        for clause in clauses:
            result = self.classify_clause(clause)
            results.append(result)
        
        return results
    
    def get_confidence_distribution(self, results: List[ClassificationResult]) -> Dict[str, float]:
        """Get distribution of confidence scores."""
        confidences = [r.confidence for r in results]
        
        return {
            'mean': sum(confidences) / len(confidences) if confidences else 0.0,
            'min': min(confidences) if confidences else 0.0,
            'max': max(confidences) if confidences else 0.0,
            'median': sorted(confidences)[len(confidences) // 2] if confidences else 0.0,
        }
    
    def get_category_distribution(self, results: List[ClassificationResult]) -> Dict[str, int]:
        """Get distribution of predicted categories."""
        distribution = {cat.value: 0 for cat in self.categories}
        
        for result in results:
            distribution[result.predicted_category.value] += 1
        
        return distribution
    
    def generate_mock_predictions(self, num_clauses: int = 50) -> List[ClassificationResult]:
        """Generate mock predictions for testing."""
        results = []
        
        for i in range(num_clauses):
            # Randomly select category
            category = random.choice(self.categories)
            confidence = random.uniform(0.65, 0.98)
            
            # Create top-k predictions
            other_categories = [c for c in self.categories if c != category]
            top_k = [(category, confidence)]
            for other_cat in random.sample(other_categories, 4):
                top_k.append((other_cat, random.uniform(0.40, confidence - 0.1)))
            
            result = ClassificationResult(
                clause_id=f"cl_{i}",
                predicted_category=category,
                confidence=confidence,
                top_k_predictions=top_k,
                explanation=f"Mock prediction for clause {i}"
            )
            results.append(result)
        
        return results
    
    def evaluate_predictions(self, 
                            predictions: List[ClassificationResult],
                            ground_truth: List[Tuple[str, RiskCategory]]) -> ClassifierMetrics:
        """Evaluate predictions against ground truth."""
        metrics = ClassifierMetrics()
        
        # Create mapping of clause_id to prediction
        pred_map = {p.clause_id: p for p in predictions}
        
        correct = 0
        per_category = {cat: {'tp': 0, 'fp': 0, 'fn': 0} for cat in self.categories}
        
        for clause_id, true_category in ground_truth:
            if clause_id in pred_map:
                prediction = pred_map[clause_id]
                
                if prediction.predicted_category == true_category:
                    correct += 1
                    per_category[true_category]['tp'] += 1
                else:
                    per_category[true_category]['fn'] += 1
                    per_category[prediction.predicted_category]['fp'] += 1
        
        # Calculate accuracy
        metrics.accuracy = correct / len(ground_truth) if ground_truth else 0.0
        
        # Calculate per-category metrics
        f1_scores = []
        for category, counts in per_category.items():
            tp = counts['tp']
            fp = counts['fp']
            fn = counts['fn']
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            metrics.per_category_metrics[category] = {
                'precision': precision,
                'recall': recall,
                'f1': f1
            }
            
            if counts['tp'] + counts['fn'] > 0:
                f1_scores.append(f1)
        
        # Calculate macro F1
        metrics.macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0
        
        return metrics
    
    def export_predictions_json(self, results: List[ClassificationResult]) -> str:
        """Export predictions as JSON."""
        output = {
            'total_clauses': len(results),
            'predictions': [r.to_dict() for r in results],
            'category_distribution': self.get_category_distribution(results),
            'confidence_distribution': self.get_confidence_distribution(results),
        }
        
        return json.dumps(output, indent=2, default=str)
    
    def generate_classification_report(self, results: List[ClassificationResult]) -> str:
        """Generate comprehensive classification report."""
        lines = ["=== LEGAL-BERT CLASSIFICATION REPORT ===\n"]
        
        lines.append(f"Total Clauses Classified: {len(results)}")
        lines.append(f"Mean Confidence: {self.get_confidence_distribution(results)['mean']:.4f}\n")
        
        category_dist = self.get_category_distribution(results)
        lines.append("Category Distribution:")
        for category, count in sorted(category_dist.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(results) * 100) if results else 0
            lines.append(f"  {category}: {count} ({percentage:.1f}%)")
        
        lines.append("\nTop Confidence Predictions:")
        sorted_by_conf = sorted(results, key=lambda x: x.confidence, reverse=True)
        for result in sorted_by_conf[:5]:
            lines.append(f"  {result.clause_id}: {result.predicted_category.value} ({result.confidence:.4f})")
        
        return "\n".join(lines)
