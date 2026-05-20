"""
Phase 4 NLP Pipeline Orchestrator - Complete Contract Intelligence Pipeline.
Integrates all NLP modules for end-to-end contract analysis.
"""

import json
import time
from typing import Optional, Dict, List
from datetime import datetime

from contract_types import ContractAnalysisResult, SeverityLevel
from layout_lm_parser import LayoutLMParser
from clause_resolver import ClauseResolver
from custom_ner import ContractNER
from legal_bert_classifier import LegalBertClassifier
from contract_risk_scorer import ContractRiskScorer
from benchmark_database import BenchmarkDatabase
from comparative_analysis import ComparativeAnalyzer


class Phase4Pipeline:
    """Complete Phase 4 NLP pipeline for contract intelligence."""
    
    def __init__(self):
        """Initialize all pipeline components."""
        self.parser = LayoutLMParser()
        self.resolver = ClauseResolver()
        self.ner = ContractNER()
        self.classifier = LegalBertClassifier()
        self.scorer = ContractRiskScorer()
        self.benchmark_db = BenchmarkDatabase()
        self.analyzer = ComparativeAnalyzer(self.benchmark_db)
        self.results = []
    
    def process_contract(
        self,
        contract_id: str,
        filename: str,
        contract_text: str,
        sector: str = "default",
        country: str = "default",
        project_value: float = 1_000_000,
        tenor_years: int = 20,
        equity_percentage: float = 30,
    ) -> ContractAnalysisResult:
        """Process contract through complete pipeline."""
        
        start_time = time.time()
        result = ContractAnalysisResult(contract_id=contract_id, filename=filename)
        
        try:
            # Step 1: Parse PDF and extract clauses
            pdf_structure = self.parser.parse_pdf(
                pdf_path=filename,
                extract_text=contract_text
            )
            result.extracted_clauses = pdf_structure.clauses
            
            # Step 2: Resolve clause cross-references
            graph = self.resolver.build_dependency_graph(result.extracted_clauses)
            
            # Step 3: Extract named entities
            entities = self.ner.extract_entities(contract_text)
            # Also extract percentages and locations
            entities.extend(self.ner.extract_percentages(contract_text))
            entities.extend(self.ner.extract_locations(contract_text))
            result.named_entities = entities
            
            # Attach entities to clauses
            for clause in result.extracted_clauses:
                clause.entities = [
                    e for e in entities
                    if e.start_pos >= clause.start_line and e.end_pos <= clause.end_line
                ]
            
            # Step 4: Classify clauses
            classification_results = self.classifier.classify_clauses(result.extracted_clauses)
            result.classification_results = classification_results
            
            # Update clause categories
            for classification in classification_results:
                clause = next(
                    (c for c in result.extracted_clauses if c.clause_id == classification.clause_id),
                    None
                )
                if clause:
                    clause.risk_category = classification.predicted_category
                    clause.confidence = classification.confidence
            
            # Step 5: Score contract risk
            result.risk_scores = self.scorer.score_contract(
                clauses=result.extracted_clauses,
                classification_results=classification_results,
                entities=entities,
                industry=sector,
                country=country
            )
            
            # Step 6: Comparative analysis against benchmarks
            result.comparative_analysis = self.analyzer.analyze_contract(
                contract_id=contract_id,
                clauses=result.extracted_clauses,
                sector=sector,
                country=country,
                project_value=project_value,
                tenor_years=tenor_years,
                equity_percentage=equity_percentage,
                milestone_count=len([c for c in result.extracted_clauses if 'milestone' in c.text.lower()])
            )
            
            # Finalize result
            result.extraction_time = time.time() - start_time
            result.processing_errors = []
            result.confidence_score = min(
                result.risk_scores.confidence,
                sum(c.confidence for c in result.extracted_clauses) / max(len(result.extracted_clauses), 1)
            )
            result.created_at = datetime.now()
            
        except Exception as e:
            result.processing_errors.append(str(e))
            result.extraction_time = time.time() - start_time
        
        self.results.append(result)
        return result
    
    def generate_executive_summary(self, result: ContractAnalysisResult) -> str:
        """Generate executive summary of analysis."""
        lines = ["=" * 60]
        lines.append("PHASE 4 NLP PIPELINE - EXECUTIVE SUMMARY")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append(f"Contract ID: {result.contract_id}")
        lines.append(f"Filename: {result.filename}")
        lines.append(f"Analysis Timestamp: {result.created_at.isoformat()}")
        lines.append("")
        
        lines.append("RISK ASSESSMENT:")
        lines.append("-" * 40)
        lines.append(f"Overall Risk Level: {result.risk_scores.overall_severity.value}")
        lines.append(f"Risk Score: {result.risk_scores.overall_score:.2f}/5.0")
        lines.append("")
        
        lines.append("EXTRACTED CONTENT:")
        lines.append("-" * 40)
        lines.append(f"Total Clauses: {len(result.extracted_clauses)}")
        lines.append(f"Named Entities: {len(result.named_entities)}")
        lines.append(f"Classification Results: {len(result.classification_results)}")
        lines.append("")
        
        if result.extracted_clauses:
            lines.append("TOP CLAUSES BY RISK:")
            sorted_clauses = sorted(
                result.extracted_clauses,
                key=lambda c: self.scorer.score_clause(c),
                reverse=True
            )
            for clause in sorted_clauses[:3]:
                score = self.scorer.score_clause(clause)
                lines.append(f"  • {clause.full_reference}: {score:.2f} ({clause.risk_category.value})")
        
        lines.append("")
        lines.append("RED FLAGS:")
        lines.append("-" * 40)
        if result.risk_scores.red_flags:
            for flag in result.risk_scores.red_flags[:5]:
                lines.append(f"  🚩 {flag}")
        else:
            lines.append("  No critical red flags detected")
        
        if result.comparative_analysis:
            lines.append("")
            lines.append("BENCHMARK COMPARISON:")
            lines.append("-" * 40)
            lines.append(f"Similarity Score: {result.comparative_analysis.similarity_score:.2%}")
            lines.append(f"Deviations: {len(result.comparative_analysis.deviations)}")
            lines.append(f"Non-Standard Terms: {len(result.comparative_analysis.non_standard_terms)}")
        
        lines.append("")
        lines.append("PROCESSING METRICS:")
        lines.append("-" * 40)
        lines.append(f"Extraction Time: {result.extraction_time:.2f}s")
        lines.append(f"Confidence Score: {result.confidence_score:.2%}")
        lines.append(f"Processing Errors: {len(result.processing_errors)}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def export_full_report_json(self, result: ContractAnalysisResult) -> str:
        """Export complete analysis as JSON."""
        return json.dumps(result.to_dict(), indent=2, default=str)
    
    def generate_pipeline_report(self) -> str:
        """Generate overall pipeline performance report."""
        lines = ["=" * 60]
        lines.append("PHASE 4 NLP PIPELINE - PERFORMANCE REPORT")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append(f"Total Contracts Processed: {len(self.results)}")
        lines.append("")
        
        if self.results:
            # Statistics
            total_clauses = sum(len(r.extracted_clauses) for r in self.results)
            total_entities = sum(len(r.named_entities) for r in self.results)
            total_time = sum(r.extraction_time for r in self.results)
            avg_confidence = sum(r.confidence_score for r in self.results) / len(self.results)
            
            lines.append("STATISTICS:")
            lines.append(f"  Total Clauses Extracted: {total_clauses}")
            lines.append(f"  Total Entities Extracted: {total_entities}")
            lines.append(f"  Total Processing Time: {total_time:.2f}s")
            lines.append(f"  Average Confidence: {avg_confidence:.2%}")
            lines.append("")
            
            # Risk distribution
            lines.append("RISK DISTRIBUTION:")
            risk_levels = {}
            for result in self.results:
                level = result.risk_scores.overall_severity.value
                risk_levels[level] = risk_levels.get(level, 0) + 1
            
            for level, count in sorted(risk_levels.items()):
                pct = (count / len(self.results) * 100)
                lines.append(f"  {level}: {count} ({pct:.1f}%)")
            
            lines.append("")
            lines.append("TOP RISKS IDENTIFIED:")
            all_red_flags = []
            for result in self.results:
                all_red_flags.extend(result.risk_scores.red_flags)
            
            # Count red flag occurrences
            flag_counts = {}
            for flag in all_red_flags:
                flag_counts[flag] = flag_counts.get(flag, 0) + 1
            
            for flag, count in sorted(flag_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                lines.append(f"  • {flag} ({count} occurrences)")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)


def create_sample_contract_text() -> str:
    """Create sample contract text for testing."""
    return """
    INFRASTRUCTURE PROJECT FINANCE AGREEMENT
    
    THIS AGREEMENT is entered into by and between PowerCorp Ltd as Sponsor and 
    International Finance Bank as Lender.
    
    SECTION 1: DEFINITIONS AND INTERPRETATIONS
    
    1.1 Project Value
    The total project amount shall be USD 500 million for the implementation of 
    renewable energy infrastructure.
    
    SECTION 2: FINANCIAL COVENANTS
    
    2.1 Debt Service Coverage Ratio
    The Sponsor shall maintain at all times a Debt Service Coverage Ratio (DSCR) 
    of not less than 1.25x on an annual basis, calculated on a rolling 12-month basis.
    
    2.2 Maximum Leverage Ratio
    The Sponsor covenants that the Leverage Ratio shall not exceed 3.5x at any time 
    during the life of this Agreement.
    
    2.3 Minimum Liquidity
    The Project shall at all times maintain minimum liquidity of not less than 
    USD 25 million in restricted accounts.
    
    SECTION 3: PROJECT MILESTONES
    
    3.1 Financial Close
    Financial Close shall be achieved by June 30, 2024.
    
    3.2 Construction Start
    Construction shall commence within 30 days of Financial Close.
    
    3.3 Commercial Operations
    The Project shall achieve Commercial Operations Date by December 31, 2025.
    
    SECTION 4: INSURANCE REQUIREMENTS
    
    4.1 Comprehensive Insurance Coverage
    The Sponsor shall procure and maintain comprehensive insurance covering all aspects 
    of the Project including construction, operation, and liability insurance.
    
    4.2 Insurance Beneficiary
    All insurance policies shall name the Lender as loss payee and additional insured.
    
    SECTION 5: TERMINATION FOR CONVENIENCE
    
    5.1 Early Termination
    Either party may not terminate this Agreement except for material breach by the 
    other party not cured within 60 days of notice.
    
    SECTION 6: ENVIRONMENTAL COMPLIANCE
    
    6.1 Environmental Liability
    The Sponsor assumes full responsibility for all environmental liabilities arising 
    from the Project.
    
    6.2 Remediation Requirements
    The Sponsor shall remediate any environmental impacts discovered during Project life.
    
    SECTION 7: DISPUTE RESOLUTION
    
    7.1 Arbitration
    All disputes shall be resolved through International Arbitration in Singapore 
    under UNCITRAL rules.
    
    SECTION 8: INTELLECTUAL PROPERTY
    
    8.1 Confidentiality
    All Project information shall be treated as confidential and proprietary.
    
    SECTION 9: PENALTIES AND REMEDIES
    
    9.1 Liquidated Damages
    In case of covenant breach, the Sponsor shall pay liquidated damages of 
    0.25% per month to the Lender.
    
    9.2 Cross-Default
    Breach of any covenant under this Agreement shall result in cross-default 
    to all other Project financing agreements.
    
    SECTION 10: COVENANTS AND OBLIGATIONS
    
    10.1 Sponsor Obligations
    The Sponsor undertakes to:
    (a) Develop and operate the Project in a professional manner
    (b) Maintain audited financial statements
    (c) Provide quarterly reports to the Lender
    (d) Comply with all laws and regulations
    
    EFFECTIVE DATE: January 15, 2024
    PARTIES: PowerCorp Ltd and International Finance Bank
    GOVERNING LAW: English Law
    """


if __name__ == "__main__":
    # Initialize pipeline
    pipeline = Phase4Pipeline()
    
    # Process sample contract
    sample_text = create_sample_contract_text()
    result = pipeline.process_contract(
        contract_id="DEMO_001",
        filename="sample_infrastructure_contract.pdf",
        contract_text=sample_text,
        sector="renewable_energy",
        country="singapore",
        project_value=500_000_000,
        tenor_years=25,
        equity_percentage=30,
    )
    
    # Print results
    print(pipeline.generate_executive_summary(result))
    print("\n" + "=" * 60 + "\n")
    print(pipeline.generate_pipeline_report())
