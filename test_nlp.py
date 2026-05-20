"""Test suite for NLP modules."""

import unittest
from nlp_module import (
    LayoutLMParser, ContractNER, LegalBERTClassifier,
    ContractRiskScorer, BenchmarkDatabase
)


class TestLayoutLMParser(unittest.TestCase):
    def setUp(self):
        self.parser = LayoutLMParser()
        self.sample_contract = """
        ARTICLE 1: DEFINITIONS
        1.1 Sponsor: ABC Infrastructure
        SECTION 2: TERMS
        2.1 Debt: USD 100 Million
        """

    def test_load_document(self):
        self.parser.document_text = self.sample_contract
        self.assertGreater(len(self.parser.document_text), 0)

    def test_extract_sections(self):
        self.parser.document_text = self.sample_contract
        sections = self.parser.extract_sections()
        self.assertGreater(len(sections), 0)


class TestContractNER(unittest.TestCase):
    def setUp(self):
        self.ner = ContractNER()

    def test_extract_sponsors(self):
        text = "Sponsor: ABC Infrastructure Inc."
        sponsors = self.ner.extract_sponsors(text)
        self.assertGreater(len(sponsors), 0)

    def test_extract_amounts(self):
        text = "Total debt: USD 250 Million"
        amounts = self.ner.extract_amounts(text)
        self.assertGreater(len(amounts), 0)


class TestLegalBERTClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = LegalBERTClassifier()

    def test_classify_clause(self):
        text = "Force majeure clause in contract"
        label_id, category, conf = self.classifier.classify_clause(text)
        self.assertEqual(label_id, 1)
        self.assertGreater(conf, 0)


if __name__ == '__main__':
    unittest.main()