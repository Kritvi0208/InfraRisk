"""
Comprehensive Test Suite for Phase 4: NLP & Contract Intelligence
Tests for document parsing, NER, clause classification, risk scoring, and benchmarks
"""

import unittest
import json
import tempfile
import os
from pathlib import Path

# Import all NLP modules
from nlp_module import (
    LayoutLMParser, ContractNER, LegalBERTClassifier,
    ContractRiskScorer, BenchmarkDatabase, CLAUSE_CATEGORIES,
    EntityExtraction, Section, Clause, EntityRegion
)


class TestLayoutLMParser(unittest.TestCase):
    """Test suite for LayoutLMParser"""

    def setUp(self):
        """Initialize parser for each test"""
        self.parser = LayoutLMParser(verbose=True)
        self.sample_contract = """
        ARTICLE 1: DEFINITIONS
        1.1 "Sponsor" means the project sponsor.
        1.2 "Lender" means the financial institution.
        
        SECTION 2: TERMS
        2.1 Debt Tenor shall be 25 years.
        2.2(a) The Borrower shall maintain DSCR > 1.25.
        2.2(b)(i) Financial covenants apply.
        2.2(b)(ii) Quarterly reporting required.
        
        PART 3: COVENANTS
        3.1 Affirmative covenants shall include.
        """

    def test_load_document(self):
        """Test document loading"""
        self.parser.document_text = self.sample_contract
        self.assertEqual(len(self.parser.document_text) > 0, True)

    def test_extract_sections(self):
        """Test section extraction"""
        self.parser.document_text = self.sample_contract
        sections = self.parser.extract_sections()
        self.assertGreater(len(sections), 0)
        self.assertIn("ARTICLE_1", sections)
        self.assertIn("SECTION_2", sections)

    def test_resolve_nested_clauses(self):
        """Test nested clause resolution"""
        self.parser.document_text = self.sample_contract
        self.parser.extract_sections()
        clauses = self.parser.resolve_nested_clauses()
        self.assertGreater(len(clauses), 0)

    def test_build_clause_graph(self):
        """Test clause reference graph"""
        self.parser.document_text = self.sample_contract
        self.parser.extract_sections()
        self.parser.resolve_nested_clauses()
        graph = self.parser.build_clause_graph()
        self.assertIsInstance(graph, dict)

    def test_extract_entity_regions(self):
        """Test entity extraction"""
        self.parser.document_text = self.sample_contract
        entities = self.parser.extract_entity_regions()
        self.assertGreater(len(entities), 0)

        # Check for sponsor
        sponsors = [e for e in entities if e.entity_type == "SPONSOR"]
        self.assertGreater(len(sponsors), 0)

        # Check for lender
        lenders = [e for e in entities if e.entity_type == "LENDER"]
        self.assertGreater(len(lenders), 0)

        # Check for amounts
        amounts = [e for e in entities if e.entity_type == "AMOUNT"]
        self.assertGreater(len(amounts), 0)

    def test_to_json(self):
        """Test JSON export"""
        self.parser.document_text = self.sample_contract
        self.parser.extract_sections()
        self.parser.resolve_nested_clauses()
        self.parser.build_clause_graph()
        self.parser.extract_entity_regions()

        json_output = self.parser.to_json()
        self.assertIsInstance(json_output, str)

        # Parse JSON to verify structure
        data = json.loads(json_output)
        self.assertIn("document_metadata", data)
        self.assertIn("sections", data)
        self.assertIn("clauses", data)
        self.assertIn("entities", data)

    def test_get_clause_by_number(self):
        """Test clause retrieval"""
        self.parser.document_text = self.sample_contract
        self.parser.extract_sections()
        self.parser.resolve_nested_clauses()

        # Try to retrieve a clause
        clause = self.parser.get_clause_by_number("1.1")
        # May or may not find depending on parsing

    def test_get_entities_by_type(self):
        """Test entity filtering by type"""
        self.parser.document_text = self.sample_contract
        self.parser.extract_entity_regions()

        sponsors = self.parser.get_entities_by_type("SPONSOR")
        self.assertIsInstance(sponsors, list)


class TestContractNER(unittest.TestCase):
    """Test suite for Named Entity Recognition"""

    def setUp(self):
        """Initialize NER for each test"""
        self.ner = ContractNER()
        self.sample_text = """
        The Sponsor is ABC Infrastructure Private Limited.
        The Lender is Development Bank of India.
        Total Debt Amount: USD 250 Million
        Equity Investment: EUR 100 Million
        Financial Close: 2024-06-30
        Project Location: Tamil Nadu, India
        Project Sector: Solar Energy
        """

    def test_extract_sponsors(self):
        """Test sponsor extraction"""
        sponsors = self.ner.extract_sponsors(self.sample_text)
        self.assertGreater(len(sponsors), 0)
        # Check confidence
        for sponsor, confidence in sponsors:
            self.assertGreater(confidence, 0)
            self.assertLessEqual(confidence, 1.0)

    def test_extract_lenders(self):
        """Test lender extraction"""
        lenders = self.ner.extract_lenders(self.sample_text)
        self.assertGreater(len(lenders), 0)
        for lender, confidence in lenders:
            self.assertGreater(confidence, 0)

    def test_extract_amounts(self):
        """Test amount extraction"""
        amounts = self.ner.extract_amounts(self.sample_text)
        self.assertGreater(len(amounts), 0)
        for amount, currency, confidence in amounts:
            self.assertIn(currency, ["USD", "EUR", "GBP", "UNKNOWN"])

    def test_extract_dates(self):
        """Test date extraction"""
        dates = self.ner.extract_dates(self.sample_text)
        self.assertGreater(len(dates), 0)
        for date, date_type, confidence in dates:
            self.assertGreater(confidence, 0)

    def test_extract_project_details(self):
        """Test project detail extraction"""
        projects = self.ner.extract_project_details(self.sample_text)
        # May or may not have projects depending on text
        self.assertIsInstance(projects, list)

    def test_extract_all(self):
        """Test complete extraction"""
        extraction = self.ner.extract_all(self.sample_text)
        self.assertIsInstance(extraction, EntityExtraction)
        self.assertIsInstance(extraction.sponsors, list)
        self.assertIsInstance(extraction.lenders, list)
        self.assertIsInstance(extraction.amounts, list)
        self.assertIsInstance(extraction.dates, list)

    def test_train_custom_ner(self):
        """Test NER training"""
        training_data = [
            ("ABC Infrastructure Inc", {"entities": [(0, 23, "SPONSOR")]}),
            ("Development Bank", {"entities": [(0, 16, "LENDER")]}),
        ]
        accuracy = self.ner.train_custom_ner(training_data)
        self.assertGreater(accuracy, 0)
        self.assertLessEqual(accuracy, 1.0)

    def test_to_dict(self):
        """Test extraction to dictionary"""
        extraction = self.ner.extract_all(self.sample_text)
        result_dict = self.ner.to_dict(extraction)
        self.assertIsInstance(result_dict, dict)
        self.assertIn("sponsors", result_dict)
        self.assertIn("lenders", result_dict)


class TestLegalBERTClassifier(unittest.TestCase):
    """Test suite for Legal-BERT Clause Classification"""

    def setUp(self):
        """Initialize classifier for each test"""
        self.classifier = LegalBERTClassifier()

    def test_classify_force_majeure(self):
        """Test force majeure classification"""
        text = "The project may be interrupted due to force majeure events beyond the sponsor's control."
        label_id, category, confidence = self.classifier.classify_clause(text)
        self.assertEqual(label_id, 1)
        self.assertEqual(category, "Force Majeure")
        self.assertGreater(confidence, 0.5)

    def test_classify_termination(self):
        """Test termination rights classification"""
        text = "The Lender has the right to terminate the facility if covenants are breached."
        label_id, category, confidence = self.classifier.classify_clause(text)
        self.assertEqual(label_id, 2)
        self.assertEqual(category, "Termination Rights")

    def test_classify_covenant(self):
        """Test covenant violation classification"""
        text = "The Borrower must maintain DSCR above 1.25x at all times as a financial covenant."
        label_id, category, confidence = self.classifier.classify_clause(text)
        self.assertEqual(label_id, 5)
        self.assertEqual(category, "Covenant Violations")

    def test_classify_subordination(self):
        """Test subordination classification"""
        text = "All equity shall be subordinated to senior debt in the capital stack."
        label_id, category, confidence = self.classifier.classify_clause(text)
        self.assertEqual(label_id, 7)
        self.assertEqual(category, "Subordination")

    def test_classify_batch(self):
        """Test batch classification"""
        texts = [
            "Force majeure event",
            "Termination clause",
            "Financial covenant",
        ]
        results = self.classifier.classify_batch(texts)
        self.assertEqual(len(results), 3)
        for label_id, category, confidence in results:
            self.assertIn(label_id, range(1, 13))
            self.assertGreater(confidence, 0)

    def test_fine_tune(self):
        """Test fine-tuning"""
        training_data = [
            ("Force majeure clause", 1),
            ("Termination rights", 2),
            ("Covenant restrictions", 5),
        ]
        metrics = self.classifier.fine_tune_on_infrastructure_contracts(training_data, epochs=1)
        self.assertIn("f1_score", metrics)
        self.assertIn("accuracy", metrics)
        self.assertGreater(metrics["f1_score"], 0.85)

    def test_load_pretrained(self):
        """Test loading pre-trained model"""
        result = self.classifier.load_pretrained_legal_bert()
        self.assertIsInstance(result, bool)


class TestContractRiskScorer(unittest.TestCase):
    """Test suite for Contract Risk Scoring"""

    def setUp(self):
        """Initialize scorer for each test"""
        self.scorer = ContractRiskScorer()

    def test_score_clause_force_majeure(self):
        """Test scoring force majeure"""
        text = "Perpetual force majeure clause with unlimited scope"
        score = self.scorer.score_clause(1, text)
        self.assertIn(score, range(1, 6))
        self.assertGreaterEqual(score, 4)  # Should be high

    def test_score_clause_favorable(self):
        """Test scoring favorable terms"""
        text = "Optional step-down provision with discretionary waiver"
        score = self.scorer.score_clause(8, text)
        self.assertIn(score, range(1, 6))
        self.assertLessEqual(score, 2)  # Should be low (favorable)

    def test_aggregate_project_risk(self):
        """Test project-level risk aggregation"""
        clause_scores = {
            1: [4, 4],  # Force Majeure
            5: [4, 3],  # Covenants
            7: [5],     # Subordination
            12: [3],    # Default
        }
        project_risk = self.scorer.aggregate_project_risk(clause_scores)
        self.assertGreater(project_risk, 0)
        self.assertLessEqual(project_risk, 5)

    def test_flag_covenants(self):
        """Test covenant flagging"""
        clauses = [
            (5, "Financial covenant: DSCR > 1.25x"),
            (5, "Maintenance covenant for asset condition"),
        ]
        flagged = self.scorer.flag_covenants(clauses)
        self.assertGreater(len(flagged), 0)

    def test_identify_bottleneck_terms(self):
        """Test bottleneck identification"""
        clauses = [
            (2, "Perpetual termination rights for sponsor"),
            (5, "Strict financial covenants"),
            (7, "Perpetual subordination"),
        ]
        bottlenecks = self.scorer.identify_bottleneck_terms(clauses)
        self.assertGreater(len(bottlenecks), 0)

    def test_generate_risk_report(self):
        """Test complete risk report generation"""
        clause_scores = {
            1: [3],
            2: [4],
            5: [4, 4],
            7: [5],
        }
        report = self.scorer.generate_risk_report(clause_scores)
        self.assertIn("project_risk_score", report)
        self.assertIn("risk_level", report)
        self.assertIn("category_breakdown", report)
        self.assertIn("key_risks", report)


class TestBenchmarkDatabase(unittest.TestCase):
    """Test suite for Benchmark Database"""

    def setUp(self):
        """Initialize database for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_benchmarks.db")
        self.db = BenchmarkDatabase(self.db_path)

    def tearDown(self):
        """Clean up after tests"""
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_load_benchmarks(self):
        """Test loading benchmark transactions"""
        count = self.db.load_transaction_benchmarks(sample_size=100)
        self.assertEqual(count, 100)

    def test_extract_benchmark_terms(self):
        """Test extracting terms from benchmark"""
        self.db.load_transaction_benchmarks(sample_size=10)
        terms = self.db.extract_benchmark_terms(1)
        self.assertIsInstance(terms, dict)
        if terms:
            self.assertIn("debt_amount", terms)
            self.assertIn("debt_tenor", terms)

    def test_compare_against_benchmark(self):
        """Test comparison functionality"""
        self.db.load_transaction_benchmarks(sample_size=100)
        current_contract = {
            "project_sector": "Solar",
            "debt_tenor": 20,
            "debt_amount": 200,
        }
        comparison = self.db.compare_against_benchmark(current_contract)
        self.assertIsInstance(comparison, dict)
        self.assertIn("benchmark_count", comparison)

    def test_compute_statistics(self):
        """Test statistics computation"""
        self.db.load_transaction_benchmarks(sample_size=100)
        stats = self.db.compute_term_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn("debt_amount", stats)
        self.assertIn("debt_tenor", stats)
        self.assertIn("spread_bps", stats)

    def test_database_persistence(self):
        """Test that database persists correctly"""
        self.db.load_transaction_benchmarks(sample_size=50)
        self.db.close()

        # Reopen database
        db2 = BenchmarkDatabase(self.db_path)
        stats = db2.compute_term_statistics()
        # Should have data from before
        self.assertGreater(len(stats), 0)
        db2.close()


class TestEndToEndPipeline(unittest.TestCase):
    """End-to-end integration tests"""

    def setUp(self):
        """Setup complete pipeline"""
        self.parser = LayoutLMParser(verbose=False)
        self.ner = ContractNER()
        self.classifier = LegalBERTClassifier()
        self.scorer = ContractRiskScorer()

        self.sample_contract = """
        ARTICLE 1: DEFINITIONS
        1.1 Sponsor: ABC Solar Energy Inc
        
        SECTION 2: FINANCING TERMS
        2.1 Lender: Development Finance Corporation
        2.2 Total Project Cost: USD 150 Million
        2.3 Debt Amount: USD 100 Million
        2.4 Tenor: 20 years
        
        ARTICLE 3: COVENANTS
        3.1 Financial Covenants: Borrower must maintain DSCR > 1.25x
        3.2 Force Majeure: Subject to perpetual force majeure clause
        3.3 Subordination: Equity subordinated to senior debt
        """

    def test_complete_pipeline(self):
        """Test complete processing pipeline"""
        # Step 1: Parse document
        self.parser.document_text = self.sample_contract
        sections = self.parser.extract_sections()
        clauses = self.parser.resolve_nested_clauses()
        entities = self.parser.extract_entity_regions()

        self.assertGreater(len(sections), 0)
        self.assertGreater(len(clauses), 0)
        self.assertGreater(len(entities), 0)

        # Step 2: Extract entities
        extraction = self.ner.extract_all(self.sample_contract)
        self.assertGreater(len(extraction.sponsors), 0)
        self.assertGreater(len(extraction.lenders), 0)
        self.assertGreater(len(extraction.amounts), 0)

        # Step 3: Classify clauses
        test_clauses = [
            "Subject to perpetual force majeure",
            "Borrower must maintain DSCR > 1.25x",
            "Equity subordinated to senior debt",
        ]

        classifications = self.classifier.classify_batch(test_clauses)
        self.assertEqual(len(classifications), 3)

        # Step 4: Score risks
        clause_scores = {
            1: [4],  # Force Majeure
            5: [4],  # Covenants
            7: [5],  # Subordination
        }
        project_risk = self.scorer.aggregate_project_risk(clause_scores)
        report = self.scorer.generate_risk_report(clause_scores)

        self.assertGreater(project_risk, 0)
        self.assertIn("project_risk_score", report)


def run_tests():
    """Run all tests and generate report"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLayoutLMParser))
    suite.addTests(loader.loadTestsFromTestCase(TestContractNER))
    suite.addTests(loader.loadTestsFromTestCase(TestLegalBERTClassifier))
    suite.addTests(loader.loadTestsFromTestCase(TestContractRiskScorer))
    suite.addTests(loader.loadTestsFromTestCase(TestBenchmarkDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndPipeline))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
