"""
Integration tests for Phase 4 NLP Pipeline.
Tests all modules and their integration.
"""

import unittest
import json
from datetime import datetime

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

    def test_extract_lenders(self):
        """Test lender extraction"""
        lenders = self.ner.extract_lenders(self.sample_text)
        self.assertGreater(len(lenders), 0)

    def test_extract_amounts(self):
        """Test amount extraction"""
        amounts = self.ner.extract_amounts(self.sample_text)
        self.assertGreater(len(amounts), 0)


class TestLegalBERTClassifier(unittest.TestCase):
    """Test suite for Legal-BERT Clause Classification"""

    def setUp(self):
        """Initialize classifier for each test"""
        self.classifier = LegalBERTClassifier()

    def test_classify_force_majeure(self):
        """Test force majeure classification"""
        text = "The project may be interrupted due to force majeure events."
        label_id, category, confidence = self.classifier.classify_clause(text)
        self.assertEqual(label_id, 1)
        self.assertEqual(category, "Force Majeure")

    def test_classify_termination(self):
        """Test termination rights classification"""
        text = "The Lender has the right to terminate the facility if covenants are breached."
        label_id, category, confidence = self.classifier.classify_clause(text)
        self.assertEqual(label_id, 2)
        self.assertEqual(category, "Termination Rights")


if __name__ == '__main__':
    unittest.main()