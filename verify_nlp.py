#!/usr/bin/env python3
"""Verify NLP module functionality"""

import sys
import traceback

def test_imports():
    """Test that all modules can be imported"""
    try:
        from nlp_module import (
            LayoutLMParser, ContractNER, LegalBERTClassifier,
            ContractRiskScorer, BenchmarkDatabase, CLAUSE_CATEGORIES
        )
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False


def test_layout_parser():
    """Test LayoutLMParser"""
    try:
        from nlp_module import LayoutLMParser
        parser = LayoutLMParser()
        sample_text = """
        ARTICLE 1: DEFINITIONS
        1.1 Sponsor means the project sponsor.
        
        SECTION 2: TERMS
        2.1 Debt Tenor shall be 20 years.
        """
        parser.document_text = sample_text
        sections = parser.extract_sections()
        clauses = parser.resolve_nested_clauses()
        entities = parser.extract_entity_regions()
        
        assert len(sections) > 0, "No sections extracted"
        print(f"✅ LayoutLMParser: {len(sections)} sections, {len(clauses)} clauses")
        return True
    except Exception as e:
        print(f"❌ LayoutLMParser error: {e}")
        return False


def test_ner():
    """Test ContractNER"""
    try:
        from nlp_module import ContractNER
        ner = ContractNER()
        text = "Sponsor: ABC Infrastructure Inc\nLender: Development Bank"
        
        sponsors = ner.extract_sponsors(text)
        lenders = ner.extract_lenders(text)
        extraction = ner.extract_all(text)
        
        assert len(sponsors) > 0, "No sponsors extracted"
        assert len(lenders) > 0, "No lenders extracted"
        print(f"✅ ContractNER: {len(sponsors)} sponsors, {len(lenders)} lenders")
        return True
    except Exception as e:
        print(f"❌ ContractNER error: {e}")
        return False


def test_classifier():
    """Test LegalBERTClassifier"""
    try:
        from nlp_module import LegalBERTClassifier, CLAUSE_CATEGORIES
        classifier = LegalBERTClassifier()
        
        # Test classification
        texts = [
            "Force majeure clause",
            "Termination rights",
            "Financial covenant",
        ]
        results = classifier.classify_batch(texts)
        
        assert len(results) == 3, "Wrong number of results"
        for label_id, category, confidence in results:
            assert 1 <= label_id <= 12, f"Invalid label: {label_id}"
            assert 0 < confidence <= 1, f"Invalid confidence: {confidence}"
        
        print(f"✅ LegalBERTClassifier: Classified {len(results)} clauses")
        return True
    except Exception as e:
        print(f"❌ LegalBERTClassifier error: {e}")
        return False


def test_scorer():
    """Test ContractRiskScorer"""
    try:
        from nlp_module import ContractRiskScorer
        scorer = ContractRiskScorer()
        
        # Test scoring
        score = scorer.score_clause(1, "Perpetual force majeure")
        assert 1 <= score <= 5, f"Invalid score: {score}"
        
        # Test aggregation
        scores = {1: [4, 4], 5: [3], 7: [5]}
        project_risk = scorer.aggregate_project_risk(scores)
        assert 1 <= project_risk <= 5, f"Invalid project risk: {project_risk}"
        
        # Test report
        report = scorer.generate_risk_report(scores)
        assert "project_risk_score" in report, "No project risk score in report"
        
        print(f"✅ ContractRiskScorer: Project risk = {project_risk:.2f}/5.0")
        return True
    except Exception as e:
        print(f"❌ ContractRiskScorer error: {e}")
        return False


def test_benchmark():
    """Test BenchmarkDatabase"""
    try:
        import tempfile
        import os
        from nlp_module import BenchmarkDatabase
        
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test.db")
        
        db = BenchmarkDatabase(db_path)
        count = db.load_transaction_benchmarks(sample_size=50)
        
        assert count == 50, f"Wrong transaction count: {count}"
        
        stats = db.compute_term_statistics()
        assert "debt_amount" in stats, "No debt statistics"
        
        db.close()
        os.remove(db_path)
        
        print(f"✅ BenchmarkDatabase: Loaded {count} transactions")
        return True
    except Exception as e:
        print(f"❌ BenchmarkDatabase error: {e}")
        return False


def test_pipeline():
    """Test complete pipeline"""
    try:
        from nlp_module import (
            LayoutLMParser, ContractNER, LegalBERTClassifier,
            ContractRiskScorer
        )
        
        sample = """
        ARTICLE 1: DEFINITIONS
        1.1 Sponsor: ABC Solar Inc
        
        SECTION 2: FINANCING
        2.1 Lender: Development Bank
        2.2 Amount: USD 200 Million
        
        ARTICLE 3: COVENANTS
        3.1 Financial covenant: DSCR > 1.25x
        """
        
        # Parse
        parser = LayoutLMParser()
        parser.document_text = sample
        sections = parser.extract_sections()
        clauses = parser.resolve_nested_clauses()
        entities = parser.extract_entity_regions()
        
        # Extract entities
        ner = ContractNER()
        extraction = ner.extract_all(sample)
        
        # Classify and score
        classifier = LegalBERTClassifier()
        scorer = ContractRiskScorer()
        
        clause_scores = {}
        for clause_key, clause in clauses.items():
            label_id, _, _ = classifier.classify_clause(clause.text)
            score = scorer.score_clause(label_id, clause.text)
            if label_id not in clause_scores:
                clause_scores[label_id] = []
            clause_scores[label_id].append(score)
        
        report = scorer.generate_risk_report(clause_scores)
        
        print(f"✅ End-to-End Pipeline: Project risk = {report['project_risk_score']:.2f}/5.0")
        return True
    except Exception as e:
        print(f"❌ End-to-End Pipeline error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  NLP MODULE VERIFICATION")
    print("=" * 70 + "\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("LayoutLMParser", test_layout_parser),
        ("ContractNER", test_ner),
        ("LegalBERTClassifier", test_classifier),
        ("ContractRiskScorer", test_scorer),
        ("BenchmarkDatabase", test_benchmark),
        ("End-to-End Pipeline", test_pipeline),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nTesting {name}...", end=" ")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status:10s} {name}")
    
    print("\n" + "─" * 70)
    print(f"  Total: {passed}/{total} tests passed ({100*passed//total}%)")
    print("=" * 70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
