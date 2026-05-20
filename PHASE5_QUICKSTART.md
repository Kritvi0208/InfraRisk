"""
PHASE 5 QUICK START GUIDE
Gamified Simulation & Dashboard - InfraRisk AI

INSTALLATION & SETUP
====================

Prerequisites:
- Python 3.10+
- pip package manager

Step 1: Install Dependencies
------------------------------
pip install streamlit plotly pandas numpy

Step 2: Verify Installation
----------------------------
python p5_test_runner.py
(Should show "✅ ALL TESTS PASSED!")

Step 3: Start Dashboard
-----------------------
streamlit run p5_streamlit_app.py

The dashboard will open at: http://localhost:8501

GAME QUICK START
================

Step 1: Select Game Mode
-------------------------
- Single Deal (Tutorial): 5 years, 1 project
- Portfolio Manager (Main): 10 years, 5-15 projects
- Crisis Manager (Expert): 4 years, handle crises
- Deal Structurer (Advanced): 2 years, optimize structure

Step 2: Configure Initial Setup
--------------------------------
- Choose risk profile
- Set debt/equity targets
- Select initial projects

Step 3: Play Each Turn
-----------------------
- Review market conditions
- Source new deals (if cash available)
- Restructure existing deals
- Manage construction delays
- Monitor DSCR and leverage
- Respond to triggered events

Step 4: Track Performance
--------------------------
- Portfolio Overview: Check total value, DSCR, defaults
- Risk Dashboard: Monitor concentration, leverage
- Scoring: Track 1,000-point score
- Leaderboard: Compare with other players

GAME MECHANICS
==============

Turn Progression:
1. Advance quarterly
2. Process cash flows
3. Trigger events (stochastic)
4. Apply shocks to affected deals
5. Update portfolio metrics
6. Calculate scores
7. Move to next quarter

DSCR (Debt Service Coverage Ratio):
- Formula: Annual EBITDA / Annual Debt Service
- Minimum: 1.25x (hard constraint)
- Target: 1.5x+ (good performance)
- Excellent: 1.8x+ (top score)

Deal Structuring:
- Set debt/equity ratio (typically 70/30)
- Choose coupon rate (5-7%)
- Tenors: 10-30 years
- Must maintain DSCR > 1.25x

Shocks from Events:
- Pandemic: Revenue -30%, Costs +20%, Delay +18mo
- Downgrade: Coupon +300bps
- Climate: CapEx +$50M, Delay +12mo
- FX Crisis: Revenue -40%
- Rate Shock: Coupon +200bps

SCORING BREAKDOWN (1,000 points)
==================================

1. PD Accuracy (250 pts)
   - No defaults: 250 pts
   - <5% default rate: 200 pts
   - 5-15% default rate: 100 pts
   - >15% default rate: Lower
   - Bonus for DSCR > 1.8x: +50 pts

2. Debt Optimization (250 pts)
   - Optimal leverage (0.60-0.75): 200 pts
   - Good DSCR coverage: +50 pts
   - Other ranges: 50-150 pts

3. ESG Integration (300 pts)
   - Green asset allocation: +100 pts
   - Carbon avoidance: +100 pts
   - Social impact: +100 pts

4. Portfolio Management (200 pts)
   - Diversification (5+ deals): +50 pts
   - Concentration control: +50 pts
   - Risk metrics (Sharpe/Sortino): +100 pts

Time Multiplier:
- 1.0x at start
- 1.2x at completion (20% bonus)

EXAMPLE GAME SESSION
====================

Session: Portfolio Manager Mode
Duration: 40 quarters (10 years)
Initial Cash: $1B

Turn 1 (Q1):
- Market: Rates 5%, Inflation 2%
- Action: Source 2 deals (Solar, Water)
- Structure: 70% debt, 30% equity
- Result: Portfolio value $250M, DSCR 1.8x

Turns 2-10 (Q2-Q10):
- Quarterly progression
- No major events
- Source 1-2 more deals
- Portfolio grows to $700M
- Average DSCR: 1.5x

Turn 11 (Q11): Pandemic Event
- Severity: 0.8
- Revenue shock: -24% on all deals
- Delay impact: 14 months construction
- Action: Restructure deals, extend tenors
- Portfolio DSCR drops to 1.2x (compliance edge)

Turns 12-20: Recovery
- Events subside
- Portfolio recovers
- DSCR returns to 1.5x+
- New deals added
- Cash reserves built

Final Turn (Q40):
- Portfolio: 8 deals, $2B value
- DSCR: 1.6x
- Defaults: 0
- ESG: 60% green assets
- Score: 850 points

DASHBOARD PAGES
================

1. Portfolio Overview
   - Key metrics (size, value, DSCR, defaults)
   - Sector breakdown (pie chart)
   - Active deals list
   - Deal cards with status

2. DSCR Trends
   - Time series of DSCR by deal
   - Compliance status (green/red line at 1.25x)
   - Deal comparison table
   - Portfolio statistics

3. Satellite Viewer
   - Project selection dropdown
   - Image carousel by quarter
   - Timeline showing progress
   - Placeholder for real imagery

4. Risk Dashboard
   - Risk heatmap (DSCR, Leverage, Default rate, Concentration)
   - Deal-level risks
   - Portfolio-level risks
   - Violation alerts

5. AI Opponent
   - AI portfolio metrics
   - Deals under management
   - Strategy profile
   - Player vs AI comparison

6. Scoring System
   - Current score breakdown
   - Component scores (250+250+300+200)
   - Progress bar
   - Scoring information

7. Game Controls
   - Mode selection
   - Mode descriptions and tips
   - Start new game button
   - Save/Load/Reset buttons
   - Game status and progress

TIPS & STRATEGIES
=================

Conservative Strategy:
- Leverage target: 0.60-0.65
- DSCR target: 1.8x+
- Fewer deals (3-5)
- Diversified sectors
- Minimize defaults
- Higher final score if successful

Aggressive Strategy:
- Leverage target: 0.70-0.75
- DSCR target: 1.25-1.5x
- More deals (8-12)
- Concentrate in high-return sectors
- Higher returns but default risk
- Requires crisis management skills

Balanced Strategy:
- Leverage target: 0.65-0.70
- DSCR target: 1.50-1.70
- Medium portfolio (5-8 deals)
- Mixed diversification
- Steady returns with manageable risk
- Recommended for most players

Crisis Management:
- Watch DSCR early warning (first sign: <1.5x)
- Extend tenors before covenant breach
- Reduce new sourcing when stressed
- Restructure troubled deals early
- Build cash reserves for emergencies

ESG Optimization:
- Target 50%+ green assets for 300pt bonus
- Focus on: Energy (solar/wind), Water, Healthcare
- Track carbon avoidance metrics
- Social impact deals (Water, Healthcare, Transport)
- Balance returns with ESG scores

TROUBLESHOOTING
================

Dashboard Won't Start:
- Ensure Streamlit is installed: pip install streamlit
- Check port 8501 is available
- Try: streamlit run p5_streamlit_app.py --logger.level=debug

Tests Fail:
- Verify Python 3.10+: python --version
- Check all imports work: python -c "import p5_game_state"
- Run individual test: python -c "from p5_test_runner import *; test_game_state()"

Game Won't Load:
- Verify all .py files are in same directory
- Check imports in p5_streamlit_app.py
- Clear cache: rm -r ~/.streamlit

Performance Issues:
- Reduce portfolio size
- Skip satellite viewer (uses placeholders)
- Run on local machine (not remote server)

DATA & STATE MANAGEMENT
=======================

Game Save Format:
- Pickle binary format
- Includes: GameState, Portfolio, Deals, History
- Location: Same directory as Python files
- Naming: game_{game_id}_{timestamp}.pkl

Leaderboard:
- In-memory during session
- Scores saved in ScoringSystem
- Player rankings updated automatically
- Top 10 displayed on Scoring page

Session Persistence:
- Streamlit session state: st.session_state
- Game state: GameState.save_to_file()
- History: GameState.turn_history (in-memory)

ADVANCED FEATURES
====================

Custom Rule Enforcement:
- OpponentRules class validates all decisions
- Hard constraints prevent invalid actions
- Violation reporting
- Compliance scoring

AI Opponent Logic:
- Risk profiles: Conservative, Balanced, Aggressive
- Epsilon-greedy action selection
- Q-learning updates
- Deal scoring algorithm

Event System:
- Probabilistic triggers
- 20 event types
- Severity sampling (uniform, normal, beta)
- Contagion effects
- Event timeline tracking

Stress Testing:
- Apply scenarios to portfolio
- Measure impact on DSCR
- Project defaults
- Recovery timeline

API OVERVIEW
=============

Game Initialization:
  state = GameState(game_id="g1", game_mode="portfolio_manager")
  engine = SimulationEngine(state)

Deal Operations:
  deal = Deal(name="Project", capex=100M, tenor=15)
  portfolio.add_deal(deal)
  portfolio.get_portfolio_dscr()

Simulation Control:
  result = engine.advance_turn()
  state.advance_quarter()
  state.is_game_over()

Scoring:
  scoring = ScoringSystem()
  breakdown = scoring.calculate_score(state, portfolio)
  scoring.record_score("player1", "game1", score, breakdown)

Rules Validation:
  rules = OpponentRules()
  valid, issues = rules.validate_deal_for_inclusion(portfolio, deal)

CONTACT & SUPPORT
==================

For issues or questions:
1. Check PHASE5_README.md for detailed documentation
2. Review test_runner.py for working examples
3. Inspect component source code for API details
4. Run dashboard in debug mode for troubleshooting

Project: InfraRisk AI - Phase 5: Gamified Simulation & Dashboard
Status: Complete ✅
Version: 5.0.0
Date: 2024
"""

if __name__ == "__main__":
    print(__doc__)
