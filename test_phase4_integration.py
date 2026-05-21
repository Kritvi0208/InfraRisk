"""
Integration tests for Phase 4 NLP Pipeline.
Tests all modules and their integration.
"""

import json
import unittest
from datetime import datetime

from benchmark_database import BenchmarkDatabase
from clause_resolver import ClauseResolver
from comparative_analysis import ComparativeAnalyzer
from contract_risk_scorer import ContractRiskScorer
from contract_types import (
    ClassificationResult,
    Clause,
    ComparativeAnalysisResult,
    ContractRiskScore,
    EntityType,
    NamedEntity,
    RiskCategory,
    SeverityLevel,
)
from custom_ner import ContractNER
from layout_lm_parser import LayoutLMParser
from legal_bert_classifier import LegalBertClassifier
from phase4_pipeline import Phase4Pipeline, create_sample_contract_text


class TestLayoutLMParser(unittest.TestCase):
    """Test PDF parsing functionality."""

    def setUp(self):
        self.parser = LayoutLMParser()
        self.sample_text = create_sample_contract_text()

    def test_parse_pdf(self):
        """Test PDF parsing."""
        structure = self.parser.parse_pdf("test.pdf", self.sample_text)

        self.assertIsNotNone(structure)
        self.assertGreater(len(structure.clauses), 0)
        self.assertGreater(structure.pages, 0)
        self.assertEqual(structure.total_text, self.sample_text)

    def test_extract_clauses(self):
        """Test clause extraction."""
        structure = self.parser.parse_pdf("test.pdf", self.sample_text)

        # Should extract clauses from sections
        self.assertGreater(len(structure.clauses), 0)

        # Check clause structure
        clause = structure.clauses[0]
        self.assertIsNotNone(clause.clause_id)
        self.assertIsNotNone(clause.full_reference)
        self.assertGreater(clause.start_line, -1)

    def test_resolve_cross_references(self):
        """Test cross-reference resolution."""
        structure = self.parser.parse_pdf("test.pdf", self.sample_text)
        graph = self.parser.resolve_cross_references(structure.clauses)

        self.assertIsNotNone(graph)
        self.assertIsInstance(graph, dict)

    def test_detect_circular_references(self):
        """Test circular reference detection."""
        structure = self.parser.parse_pdf("test.pdf", self.sample_text)
        circular = self.parser.detect_circular_references(structure.clauses)

        self.assertIsInstance(circular, list)

    def test_clause_summary(self):
        """Test clause summary generation."""
        structure = self.parser.parse_pdf("test.pdf", self.sample_text)
        summary = self.parser.generate_clause_summary(structure.clauses)

        self.assertIsNotNone(summary)
        self.assertGreater(len(summary), 0)

    def test_extract_to_json(self):
        """Test JSON export."""
        structure = self.parser.parse_pdf("test.pdf", self.sample_text)
        json_str = self.parser.extract_to_json(structure.clauses)

        data = json.loads(json_str)
        self.assertIn("clauses", data)
        self.assertGreater(len(data["clauses"]), 0)


class TestClauseResolver(unittest.TestCase):
    """Test clause resolution."""

    def setUp(self):
        self.parser = LayoutLMParser()
        self.resolver = ClauseResolver()
        self.sample_text = create_sample_contract_text()

    def test_build_dependency_graph(self):
        """Test dependency graph building."""
        structure = self.parser.parse_pdf("test.pdf", self.sample_text)
        graph = self.resolver.build_dependency_graph(structure.clauses)

        self.assertIsNotNone(graph)
        self.assertGreater(len(graph.clauses), 0)

    def test_resolve_clause_reference(self):
        """Test clause reference resolution."""
        structure = self.parser.parse_pdf("test.pdf", self.sample_text)
        self.resolver.build_dependency_graph(structure.clauses)

        if structure.clauses:
            clause_id = structure.clauses[0].clause_id
            resolution = self.resolver.resolve_clause_reference(clause_id)

            self.assertIsNotNone(resolution)
            self.assertIn("direct_references", resolution)
            self.assertIn("transitive_references", resolution)


class TestCustomNER(unittest.TestCase):
    """Test Named Entity Recognition."""

    def setUp(self):
        self.ner = ContractNER()
        self.sample_text = create_sample_contract_text()

    def test_extract_entities(self):
        """Test entity extraction."""
        entities = self.ner.extract_entities(self.sample_text)

        self.assertGreater(len(entities), 0)
        self.assertTrue(all(isinstance(e, NamedEntity) for e in entities))

    def test_extract_amounts(self):
        """Test amount extraction."""
        entities = self.ner._extract_amounts(self.sample_text)

        self.assertGreater(len(entities), 0)
        self.assertTrue(all(e.entity_type == EntityType.AMOUNT for e in entities))

    def test_extract_percentages(self):
        """Test percentage extraction."""
        entities = self.ner.extract_percentages(self.sample_text)

        self.assertGreater(len(entities), 0)
        self.assertTrue(all(e.entity_type == EntityType.PERCENTAGE for e in entities))

    def test_training_data_generation(self):
        """Test training data generation."""
        training_data = self.ner.generate_training_data(num_samples=50)

        self.assertEqual(len(training_data), 50)
        self.assertTrue(all("text" in item for item in training_data))
        self.assertTrue(all("entities" in item for item in training_data))


class TestLegalBertClassifier(unittest.TestCase):
    """Test Legal BERT classification."""

    def setUp(self):
        self.parser = LayoutLMParser()
        self.classifier = LegalBertClassifier()
        self.sample_text = create_sample_contract_text()

    def test_classify_clause(self):
        """Test single clause classification."""
        structure = self.parser.parse_pdf("test.pdf", self.sample_text)

        if structure.clauses:
            clause = structure.clauses[0]
            result = self.classifier.classify_clause(clause)

            self.assertIsNotNone(result)
            self.assertIsInstance(result.predicted_category, RiskCategory)
            self.assertGreaterEqual(result.confidence, 0.0)
            self.assertLessEqual(result.confidence, 1.0)

    def test_classify_clauses(self):
        """Test multiple clause classification."""
        structure = self.parser.parse_pdf("test.pdf", self.sample_text)
        results = self.classifier.classify_clauses(structure.clauses)

        self.assertEqual(len(results), len(structure.clauses))
        self.assertTrue(all(isinstance(r, ClassificationResult) for r in results))

    def test_mock_predictions(self):
        """Test mock prediction generation."""
        results = self.classifier.generate_mock_predictions(num_clauses=50)

        self.assertEqual(len(results), 50)
        self.assertTrue(all(r.confidence > 0 for r in results))


class TestContractRiskScorer(unittest.TestCase):
    """Test contract risk scoring."""

    def setUp(self):
        self.parser = LayoutLMParser()
        self.classifier = LegalBertClassifier()
        self.ner = ContractNER()
        self.scorer = ContractRiskScorer()
        self.sample_text = create_sample_contract_text()

    def test_score_contract(self):
        """Test contract scoring."""
        structure = self.parser.parse_pdf("test.pdf", self.sample_text)
        classifications = self.classifier.classify_clauses(structure.clauses)
        entities = self.ner.extract_entities(self.sample_text)

        risk_score = self.scorer.score_contract(
            clauses=structure.clauses,
            classification_results=classifications,
            entities=entities,
        )

        self.assertIsNotNone(risk_score)
        self.assertIsInstance(risk_score.overall_severity, SeverityLevel)
        self.assertGreaterEqual(risk_score.overall_score, 1.0)
        self.assertLessEqual(risk_score.overall_score, 5.0)


class TestBenchmarkDatabase(unittest.TestCase):
    """Test benchmark database."""

    def setUp(self):
        self.db = BenchmarkDatabase()

    def test_database_initialization(self):
        """Test database initialization."""
        self.assertGreater(len(self.db.transactions), 0)

    def test_find_similar_deals(self):
        """Test similar deals search."""
        comparables = self.db.find_similar_deals(
            sector="renewable_energy",
            country="india",
            project_value=500_000_000,
            tenor_years=20,
            tolerance=0.25,
            max_results=5,
        )

        self.assertLessEqual(len(comparables), 5)

    def test_sector_statistics(self):
        """Test sector statistics."""
        stats = self.db.get_sector_statistics("renewable_energy")

        self.assertGreater(stats.get("count", 0), 0)
        self.assertIn("avg_project_value", stats)
        self.assertIn("avg_risk_score", stats)

    def test_outlier_detection(self):
        """Test outlier detection."""
        outliers = self.db.detect_outliers(
            sector="renewable_energy", country="india", std_threshold=2.0
        )

        self.assertIsInstance(outliers, list)


class TestComparativeAnalyzer(unittest.TestCase):
    """Test comparative analysis."""

    def setUp(self):
        self.db = BenchmarkDatabase()
        self.analyzer = ComparativeAnalyzer(self.db)
        self.parser = LayoutLMParser()
        self.sample_text = create_sample_contract_text()

    def test_analyze_contract(self):
        """Test comparative analysis."""
        structure = self.parser.parse_pdf("test.pdf", self.sample_text)

        analysis = self.analyzer.analyze_contract(
            contract_id="TEST_001",
            clauses=structure.clauses,
            sector="renewable_energy",
            country="india",
            project_value=500_000_000,
            tenor_years=20,
            equity_percentage=30,
            milestone_count=3,
        )

        self.assertIsNotNone(analysis)
        self.assertIsInstance(analysis, ComparativeAnalysisResult)
        self.assertGreaterEqual(analysis.similarity_score, 0.0)
        self.assertLessEqual(analysis.similarity_score, 1.0)


class TestPhase4Pipeline(unittest.TestCase):
    """Test complete pipeline integration."""

    def setUp(self):
        self.pipeline = Phase4Pipeline()
        self.sample_text = create_sample_contract_text()

    def test_process_contract(self):
        """Test end-to-end contract processing."""
        result = self.pipeline.process_contract(
            contract_id="TEST_001",
            filename="test_contract.pdf",
            contract_text=self.sample_text,
            sector="renewable_energy",
            country="india",
            project_value=500_000_000,
            tenor_years=25,
            equity_percentage=30,
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.contract_id, "TEST_001")
        self.assertGreater(len(result.extracted_clauses), 0)
        self.assertGreater(len(result.named_entities), 0)
        self.assertGreater(len(result.classification_results), 0)
        self.assertIsNotNone(result.risk_scores)
        self.assertIsNotNone(result.comparative_analysis)
        self.assertEqual(len(result.processing_errors), 0)

    def test_generate_executive_summary(self):
        """Test executive summary generation."""
        result = self.pipeline.process_contract(
            contract_id="TEST_001",
            filename="test_contract.pdf",
            contract_text=self.sample_text,
        )

        summary = self.pipeline.generate_executive_summary(result)

        self.assertIsNotNone(summary)
        self.assertIn(result.contract_id, summary)
        self.assertIn("Risk", summary)

    def test_export_json(self):
        """Test JSON export."""
        result = self.pipeline.process_contract(
            contract_id="TEST_001",
            filename="test_contract.pdf",
            contract_text=self.sample_text,
        )

        json_str = self.pipeline.export_full_report_json(result)
        data = json.loads(json_str)

        self.assertIsNotNone(data)
        self.assertEqual(data["contract_id"], "TEST_001")
        self.assertIn("extracted_clauses", data)
        self.assertIn("risk_scores", data)


def run_all_tests():
    """Run all integration tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLayoutLMParser))
    suite.addTests(loader.loadTestsFromTestCase(TestClauseResolver))
    suite.addTests(loader.loadTestsFromTestCase(TestCustomNER))
    suite.addTests(loader.loadTestsFromTestCase(TestLegalBertClassifier))
    suite.addTests(loader.loadTestsFromTestCase(TestContractRiskScorer))
    suite.addTests(loader.loadTestsFromTestCase(TestBenchmarkDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestComparativeAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase4Pipeline))

    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


if __name__ == "__main__":
    result = run_all_tests()

    # Print summary
    print("\n" + "=" * 70)
    print("TEST EXECUTION SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )
    print("=" * 70)
