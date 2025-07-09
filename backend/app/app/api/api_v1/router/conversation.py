import random

from fastapi import APIRouter, Depends
import openai
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.db_session import get_db
from app.models.conversation import Conversation
from app.models.user import User
from app.core.response import resp_200, resp_401
import json

router = APIRouter()

api_keys = ['f1cbcbfc-b023-4743-b959-47a625a8852f', '7bd2d286-06d5-494d-9b8a-e6492add377e',
            'd055fb6c-0c4e-4e7d-8ddb-447bdb19d6e4', 'b83ced09-7a1d-4e4d-94eb-7434d8afe798']

macro_environemnt = """
As of July 2025, the global economy is navigating a complex cycle characterized by high interest rates, moderate yet persistent inflation, and slowing economic growth. The U.S. Federal Reserve has maintained its benchmark interest rate in the range of 4.25% to 4.5%, with rate-cut expectations being postponed to curb core inflation, which remains above the long-term target of 2%. The European Central Bank and the Bank of England also continue their tightening stances, resulting in an overall restrictive monetary policy environment.

Although global inflation has eased from the peaks of 2023–2024, energy, food, and service prices still exert pressure on most economies, with core inflation remaining around 4%.

Global economic growth momentum has weakened. The IMF projects global GDP growth at only 3.2% in 2025, with the U.S. economy slowing to 1.5%. The Eurozone and Japan face sluggish growth, while China, despite policy stimulus, is expected to recover modestly to around 4.5%, still below pre-pandemic levels.

Trade tensions have intensified, with the U.S. imposing additional tariffs on multiple countries, driving continued restructuring of global supply chains and dampening corporate investment confidence. Market volatility has increased, and risk aversion has risen, leading to capital inflows into safe-haven assets such as gold and bonds. Gold prices have surged more than 25% year-to-date, reaching new all-time highs above USD 3,300 per ounce.

The U.S. dollar has weakened significantly, depreciating by approximately 11% year-to-date—its largest annual decline since 1973—due to diverging economic outlooks, widening trade deficits, and a diminishing interest rate advantage. This trend has put pressure on emerging market currencies, forcing some countries to adopt defensive rate hikes or cuts to stabilize exchange rates.

Against this backdrop, global asset performance has shown significant divergence: U.S. large-cap indices remain relatively resilient, supported by the technology and artificial intelligence sectors, though valuation risks are accumulating; the bond market has seen price rebounds due to high interest rates and capital rotation; real estate and highly leveraged assets are generally under pressure. Diversification and risk control have become crucial in asset allocation strategies.
"""


def get_financial_prompt(user_data):
    financial_prompt = f"""
    Role:
    You are a professional virtual financial analyst.

    Task:
    Generate a personalized report based on the given [user data] and [macroeconomic background], including [financial profile], [investment strategy], and [specific ETF recommendations].

    Analysis Framework:
    All your analyses must revolve around the following five core variables:
        Risk-Return Profile
        Investment Horizon
        Financial Strength & Capacity
        Liquidity Needs
        Investment Sophistication

    Inputs:
    User Data: {user_data}
    Macro Environment: {macro_environemnt}
    ETF Database: (Assumed to be connected) You can access various performance indicators of ETFs, such as returns, volatility, maximum drawdown, Sharpe ratio, expense ratio, liquidity, etc.

    Output Requirements:
    Please strictly follow the four-part structure below and use Markdown formatting:

    1. Investor Profile

    Summary in One Sentence: Directly state the user's investor type, for example: "Stable Growth Investor" or "Aggressive Long-term Investor."
    Key Insights: Briefly explain how the five key variables shape this profile.

    2. Investment Strategy

    Macro Context: Briefly describe how the current macroeconomic environment affects asset allocation.
    Allocation Framework: Propose a clear asset allocation strategy, such as the “Core-Satellite” strategy, and provide approximate proportions (e.g., 70% core, 30% satellite).

    3. ETF Recommendations

    Recommend 3 to 5 specific ETFs.

    For each ETF, you must include:

    Name (Ticker Symbol)
    Portfolio Role & Proportion (e.g., Core Asset, 40%)
    Key Reason: This is critical. You must clearly connect the ETF’s quantitative metric (e.g., "low volatility," "high Sharpe ratio") with the user's personal trait (e.g., "conservative risk tolerance," "pursuit of long-term growth") in one sentence.
    Template: Recommend [ETF Name] because its [ETF metric, e.g., low volatility] aligns perfectly with your [user trait, e.g., conservative risk tolerance].

    4. Disclaimer
    Include a standard investment risk disclaimer at the end.

    ETF Data List (Plain Text Format - For Prompt Use)

    A-share Broad-based Index ETFs
    Code: 510050, Name: SSE 50 ETF, Focus: Large-cap blue-chip leaders, Features: Value/Defensive/Low Volatility, Key Metrics: Dividend yield, low volatility, correlation with the broad market
    Code: 510300, Name: CSI 300 ETF, Focus: A-share market representative, Features: Steady Growth/Medium Volatility, Key Metrics: Benchmark returns, liquidity, expense ratio
    Code: 159919, Name: CSI 300 ETF (Shenzhen-listed), Focus: A-share market representative, Features: Steady Growth/Medium Volatility, Key Metrics: Benchmark returns, liquidity, expense ratio
    Code: 510500, Name: CSI 500 ETF, Focus: Mid-cap growth stocks, Features: Steady Growth/Medium Volatility, Key Metrics: Growth potential, possible excess returns over CSI 300
    Code: 159949, Name: ChiNext 50 ETF, Focus: Core leaders of ChiNext, Features: High Growth/High Volatility, Key Metrics: Annualized returns, growth expectations, high volatility
    Code: 588000, Name: STAR 50 ETF, Focus: Core leaders of STAR Market, Features: High Growth/High Volatility, Key Metrics: Technology attributes, high volatility, policy-driven
    Code: 159922, Name: CSI Dividend ETF, Focus: High dividend stocks, Features: High Dividend/Low to Medium Volatility, Key Metrics: Dividend yield, low drawdown, Sharpe ratio
    Code: 510880, Name: Dividend ETF (Shanghai-listed), Focus: High dividend stocks, Features: High Dividend/Low to Medium Volatility, Key Metrics: Dividend yield, low drawdown, Sharpe ratio
    Code: 159937, Name: Bosera Gold ETF, Focus: Gold assets, Features: Safe Haven/Special Market Cycles, Key Metrics: Low correlation with stocks, inflation hedge

    A-share Sector/Theme ETFs
    Code: 159928, Name: Consumer ETF, Focus: Consumer sector, Features: Steady Growth/Medium Volatility, Key Metrics: Sensitivity to economic cycles, long-term growth
    Code: 512690, Name: Liquor ETF, Focus: Liquor industry, Features: Steady Growth/Medium Volatility, Key Metrics: Brand moat, profitability, valuation
    Code: 159929, Name: Healthcare ETF, Focus: Healthcare industry, Features: High Growth/High Volatility, Key Metrics: Aging population trend, R&D investment, policy impact
    Code: 512170, Name: Medical Devices ETF, Focus: Medical devices, Features: High Growth/High Volatility, Key Metrics: Focus on equipment and technology, policy impact
    Code: 512000, Name: Brokerage ETF, Focus: Securities industry, Features: High Growth/High Volatility, Key Metrics: Highly sensitive to market cycles, high Beta
    Code: 512880, Name: Banking ETF, Focus: Banking industry, Features: Value/Defensive/Low Volatility, Key Metrics: Dividend yield, undervaluation, macroeconomic linkage
    Code: 159995, Name: Semiconductor ETF, Focus: Semiconductor industry, Features: High Growth/High Volatility, Key Metrics: Technology cycles, domestic substitution, high volatility
    Code: 512480, Name: Semiconductor ETF, Focus: Semiconductor industry, Features: High Growth/High Volatility, Key Metrics: Technology cycles, domestic substitution, high volatility
    Code: 515700, Name: New Energy Vehicle ETF, Focus: New energy vehicle supply chain, Features: High Growth/High Volatility, Key Metrics: Industry penetration rate, technology iteration, high volatility
    Code: 159863, Name: Carbon Neutral ETF, Focus: Clean energy/Environmental protection, Features: High Growth/High Volatility, Key Metrics: Policy-driven, long-term trend, high volatility
    Code: 512660, Name: Defense ETF, Focus: National defense and military industry, Features: High Growth/High Volatility, Key Metrics: Event-driven, high volatility

    Hong Kong/China Concept ETFs
    Code: 513180, Name: Hang Seng Tech ETF, Focus: Hong Kong tech giants, Features: High Growth/High Volatility, Key Metrics: Platform economy policies, high volatility, valuation recovery potential
    Code: 513050, Name: China Internet ETF, Focus: China internet giants, Features: High Growth/High Volatility, Key Metrics: Platform economy policies, China-US relations impact
    Code: 159920, Name: Hang Seng ETF, Focus: Overall Hong Kong market, Features: Steady Growth/Medium Volatility, Key Metrics: Valuation level, correlation with A-shares, liquidity

    US Broad-based/Factor ETFs
    Code: 513100, Name: Nasdaq 100 ETF (China-listed), Focus: Nasdaq 100 (Domestic version), Features: High Growth/High Volatility, Key Metrics: Global tech trends, high returns and volatility
    Code: 513500, Name: S&P 500 ETF (China-listed), Focus: S&P 500 (Domestic version), Features: Steady Growth/Medium Volatility, Key Metrics: Global economic barometer, long-term stable growth
    Code: QQQ, Name: Nasdaq 100, Focus: US tech giants, Features: High Growth/High Volatility, Key Metrics: Global tech trends, high returns and volatility
    Code: SPY, Name: S&P 500, Focus: US market benchmark, Features: Steady Growth/Medium Volatility, Key Metrics: Global economic barometer, long-term stable growth
    Code: VTI, Name: Total US Market ETF, Focus: Entire US equity market, Features: Steady Growth/Medium Volatility, Key Metrics: Broad diversification, includes small and mid-caps
    Code: DIA, Name: Dow Jones 30 ETF, Focus: US large-cap blue-chip stocks, Features: Value/Defensive/Low Volatility, Key Metrics: Industrial and financial giants, mature stability
    Code: VTV, Name: Value ETF, Focus: US large-cap value stocks, Features: Value/Defensive/Low Volatility, Key Metrics: Suitable during rate hikes, focuses on valuation and dividends
    Code: VUG, Name: Growth ETF, Focus: US large-cap growth stocks, Features: High Growth/High Volatility, Key Metrics: Suitable during rate cuts, focuses on revenue growth
    Code: VYM, Name: High Dividend ETF, Focus: US high-dividend stocks, Features: High Dividend/Low to Medium Volatility, Key Metrics: Stable cash flow, strong defensiveness

    Global/Other Market ETFs
    Code: VT, Name: Global Stock ETF, Focus: Global diversification, Features: Steady Growth/Medium Volatility, Key Metrics: Ultimate diversification tool, one-click global investment
    Code: VEA, Name: Developed Markets (Ex-US) ETF, Focus: Europe, Japan, etc., Features: Steady Growth/Medium Volatility, Key Metrics: Diversifies US market risk
    Code: VWO, Name: Emerging Markets ETF, Focus: China, India, Brazil, etc., Features: High Growth/High Volatility, Key Metrics: High growth potential with high risk
    Code: MCHI, Name: MSCI China ETF, Focus: A-shares, Hong Kong stocks, China ADRs, Features: Steady Growth/Medium Volatility, Key Metrics: China asset allocation from foreign perspective

    Bond/Fixed Income ETFs
    Code: 511260, Name: 10-Year Government Bond ETF, Focus: China long-term government bonds, Features: Defensive/Very Low Volatility, Key Metrics: Highly sensitive to interest rates, negative correlation with stocks, safe haven
    Code: 511010, Name: Government Bond ETF, Focus: Chinese government bonds (various terms), Features: Defensive/Very Low Volatility, Key Metrics: High liquidity, pure risk-free rate asset
    Code: 511380, Name: Municipal Investment Bond ETF, Focus: Chinese municipal investment bonds, Features: Stable Income/Low to Medium Volatility, Key Metrics: Higher yield than government bonds, some credit risk
    Code: AGG, Name: US Aggregate Bond ETF, Focus: Overall US bond market, Features: Defensive/Low Volatility, Key Metrics: Excellent portfolio stabilizer
    Code: LQD, Name: US Investment Grade Corporate Bond ETF, Focus: US high-credit corporate bonds, Features: Defensive/Low Volatility, Key Metrics: Higher yield than government bonds, low credit risk
    Code: SHY, Name: US Short-term Treasury ETF, Focus: 1-3 year US Treasury bonds, Features: Cash Equivalent/Very Low Volatility, Key Metrics: Extremely high liquidity, very low risk

    """
    return financial_prompt


def get_history_conversation(username, model, db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(
        and_(Conversation.username == username, Conversation.model == model)).order_by(Conversation.id).all()
    history = []
    for conv in conversations:
        history.append({"role": "user", "content": conv.user_input})
        history.append({"role": "assistant", "content": conv.output})
    return history


def generate_user_profile_summary(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    age_map = [
        "Below 25",
        "25–35",
        "36–45",
        "46–55",
        "Above 55"
    ]
    family_status_map = [
        "Single",
        "Married without children",
        "Married with children",
        "Divorced",
        "Widowed"
    ]
    annual_income_household_map = [
        "Below ¥200,000",
        "¥200,000 – ¥500,000",
        "¥500,000 – ¥1,000,000",
        "¥1,000,000 – ¥2,000,000",
        "Over ¥2,000,000"
    ]
    annual_disposable_surplus_map = [
        "Below ¥50,000",
        "¥50,000 – ¥150,000",
        "¥150,000 – ¥300,000",
        "¥300,000 – ¥500,000",
        "Over ¥500,000"
    ]
    total_assets_map = [
        "Below ¥500,000",
        "¥500,000 – ¥1,000,000",
        "¥1,000,000 – ¥3,000,000",
        "¥3,000,000 – ¥5,000,000",
        "Over ¥5,000,000"
    ]
    liabilities_map = [
        "No liabilities",
        "Minor debts",
        "Mortgage/car loan, manageable",
        "Large debts",
        "Heavily indebted"
    ]
    emergency_fund_map = [
        "None",
        "Less than 3 months",
        "3–6 months",
        "6–12 months",
        "More than 12 months"
    ]
    investment_experience_map = [
        "None",
        "Basic",
        "Moderate",
        "Advanced",
        "Professional"
    ]
    investment_period_map = [
        "Less than 1 year",
        "1–3 years",
        "3–5 years",
        "5–10 years",
        "Over 10 years"
    ]
    risk_tolerance_attitude_map = [
        "Very conservative",
        "Conservative",
        "Moderate",
        "Aggressive",
        "Very aggressive"
    ]
    expected_return_range_map = [
        "Less than 4%",
        "4% – 6%",
        "6% – 8%",
        "8% – 12%",
        "Over 12%"
    ]
    max_drawdown_tolerance_map = [
        "Less than 5%",
        "5% – 10%",
        "10% – 15%",
        "15% – 20%",
        "Over 20%"
    ]
    liquidity_needs_short_term_map = [
        "No",
        "Yes, within ¥100,000",
        "¥100,000 – ¥300,000",
        "¥300,000 – ¥500,000",
        "Over ¥500,000"
    ]

    def labelize_multi(choice_list):
        label_map = {
            'A': "Capital preservation",
            'B': "Wealth accumulation",
            'C': "Retirement planning",
            'D': "Child education",
            'E': "Short-term consumption"
        }
        return ", ".join(label_map.get(i) for i in json.loads(choice_list))

    def labelize_preferences(choice_list):
        pref_map = {
            'A': "Prefer ETFs as core allocation",
            'B': "Avoid crypto/P2P/high risk",
            'C': "Prefer ESG investments",
            'D': "Avoid specific sectors",
            'E': "No restrictions"
        }
        return ", ".join(pref_map.get(i) for i in json.loads(choice_list))

    def labelize_portfolio(portfolio: list, financial_other):
        portfolio_map = {
            'A': "Bank savings",
            'B': "Money market funds",
            'C': "Mutual funds / ETFs",
            'D': "Stocks",
            'E': "Insurance"
        }
        labeled = []
        for item in json.loads(portfolio):
            if item == 'F':
                labeled.append(f"Other: {financial_other}")
            elif item == 'G':
                labeled.append("None")
            else:
                labeled.append(portfolio_map.get(item))
        return ", ".join(labeled)

    summary = {
        "information": (
            f"My age: {age_map[user.age]}\n"
            f"My family status: {family_status_map[user.family_status]}\n"
            f"My household annual income: {annual_income_household_map[user.annual_income_household]}\n"
            f"My annual disposable surplus: {annual_disposable_surplus_map[user.annual_disposable_surplus]}\n"
            f"My total assets: {total_assets_map[user.total_assets]}\n"
            f"My financial portfolio: {labelize_portfolio(user.existing_financial_portfolio, user.financial_other)}\n"
            f"My debt status: {liabilities_map[user.liabilities]}\n"
            f"My emergency fund status: {emergency_fund_map[user.emergency_fund]}\n"
            f"My investment experience: {investment_experience_map[user.investment_experience]}\n"
            f"My investment horizon: {investment_period_map[user.investment_period]}\n"
            f"My investment goals: {labelize_multi(user.investment_goals)}\n"
            f"My risk tolerance attitude: {risk_tolerance_attitude_map[user.risk_tolerance_attitude]}\n"
            f"My expected annual return: {expected_return_range_map[user.expected_return_range]}\n"
            f"My maximum acceptable drawdown: {max_drawdown_tolerance_map[user.max_drawdown_tolerance]}\n"
            f"My investment preferences/restrictions: {labelize_preferences(user.investment_preference_restrictions)}\n"
            f"My expected short-term liquidity needs: {liquidity_needs_short_term_map[user.liquidity_needs_short_term]}"
        )
    }
    return summary


def generate_user_prompt(username: str, db: Session = Depends(get_db)):
    prompt = get_financial_prompt(generate_user_profile_summary(username, db)['information'])

    return prompt


@router.get('/load')
async def load_history_conversation(username: str, model: str, db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(
        and_(Conversation.username == username, Conversation.model == model)).all()
    history = []
    for i in range(len(conversations)):
        history.append({'user': conversations[i].user_input, 'assistant': conversations[i].output,
                        'model': conversations[i].model})
    return resp_200(data=history)


@router.get('/suggest', summary='Suggest ETFs based on search query')
async def suggest(model: str, message: str, username: str, db: Session = Depends(get_db)):
    client = openai.OpenAI(
        api_key=api_keys[random.randint(0, len(api_keys) - 1)],
        base_url="https://api.sambanova.ai/v1",
    )
    history = get_history_conversation(username, model, db)[-5:]
    messages = [{"role": "system", "content": generate_user_prompt(username, db)}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
        top_p=0.1,
        max_tokens=4096
    )
    output = response.choices[0].message.content

    db_conversation = Conversation(
        username=username,
        user_input=message,
        output=output,
        model=model
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return resp_200(data=response.choices[0].message.content)
