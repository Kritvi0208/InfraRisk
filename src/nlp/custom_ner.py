"""Custom Named Entity Recognition for contracts.

9 entity types: Sponsor, Lender, Amount, Milestone, Condition, Guarantee, Covenant, Date, Location
"""

from typing import List, Tuple

class CustomNER:
    """NER for 9 contract entity types."""
    
    entity_types = [
        'SPONSOR', 'LENDER', 'AMOUNT', 'MILESTONE', 'CONDITION',
        'GUARANTEE', 'COVENANT', 'DATE', 'LOCATION'
    ]
    
    def extract(self, text: str) -> List[Tuple[str, str]]:
        """Extract entities from contract text."""
        # Mock extraction
        entities = [
            ('XYZ Ltd', 'SPONSOR'),
            ('World Bank', 'LENDER'),
            ('$500 million', 'AMOUNT'),
            ('Project completion by 2026', 'MILESTONE'),
            ('Subject to environmental approval', 'CONDITION'),
            ('Government guarantee', 'GUARANTEE'),
            ('Maintain debt service reserve', 'COVENANT'),
            ('2026-05-19', 'DATE'),
            ('India', 'LOCATION'),
        ]
        return entities
