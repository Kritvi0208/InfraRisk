"""Quick Phase 4 Demo - Run End-to-End Pipeline"""

import sys
sys.path.insert(0, 'c:\\Users\\kayri\\OneDrive - IIT BHU\\Desktop\\InfraRiskAI')

try:
    from phase4_pipeline import Phase4Pipeline, create_sample_contract_text
    
    print("=" * 70)
    print("PHASE 4 NLP PIPELINE - QUICK DEMO")
    print("=" * 70)
    print()
    
    # Initialize pipeline
    print("1. Initializing Phase 4 NLP Pipeline...")
    pipeline = Phase4Pipeline()
    print("   ✓ Pipeline initialized")
    print()
    
    # Get sample contract text
    print("2. Loading sample contract...")
    sample_text = create_sample_contract_text()
    print(f"   ✓ Contract loaded ({len(sample_text)} characters)")
    print()
    
    # Process contract
    print("3. Processing contract through pipeline...")
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
    print("   ✓ Contract processed successfully")
    print()
    
    # Print results
    print("4. Extraction Results:")
    print(f"   • Clauses Extracted: {len(result.extracted_clauses)}")
    print(f"   • Entities Found: {len(result.named_entities)}")
    print(f"   • Classifications: {len(result.classification_results)}")
    print(f"   • Processing Time: {result.extraction_time:.2f}s")
    print(f"   • Confidence: {result.confidence_score:.2%}")
    print()
    
    # Print risk assessment
    print("5. Risk Assessment:")
    print(f"   • Overall Severity: {result.risk_scores.overall_severity.value}")
    print(f"   • Risk Score: {result.risk_scores.overall_score:.2f}/5.0")
    print(f"   • Red Flags: {len(result.risk_scores.red_flags)}")
    print(f"   • Green Flags: {len(result.risk_scores.green_flags)}")
    print()
    
    # Print clauses
    if result.extracted_clauses:
        print("6. Sample Extracted Clauses:")
        for clause in result.extracted_clauses[:3]:
            print(f"   • {clause.full_reference}: {clause.title[:50]}")
    print()
    
    # Print entities
    if result.named_entities:
        print("7. Sample Extracted Entities:")
        entity_types = {}
        for entity in result.named_entities:
            entity_type = entity.entity_type.value
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        for entity_type, count in sorted(entity_types.items()):
            print(f"   • {entity_type}: {count}")
    print()
    
    # Print benchmark comparison
    if result.comparative_analysis:
        print("8. Benchmark Comparison:")
        print(f"   • Similarity Score: {result.comparative_analysis.similarity_score:.2%}")
        print(f"   • Deviations Found: {len(result.comparative_analysis.deviations)}")
        print(f"   • Non-Standard Terms: {len(result.comparative_analysis.non_standard_terms)}")
    print()
    
    # Print full report
    print("9. Full Executive Summary:")
    print("-" * 70)
    summary = pipeline.generate_executive_summary(result)
    print(summary)
    
    print()
    print("=" * 70)
    print("✅ PHASE 4 PIPELINE EXECUTION SUCCESSFUL")
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
