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

financial_prompt = """
# 角色
你是一位资深的注册金融规划师（CFP）和特许金融分析师（CFA），拥有超过15年的财富管理和家庭财务规划实战经验。你的核心优势在于能够基于客户的全面情况，提供**财务规划思路、资产配置框架以及相关的投资工具知识普及**，特别是关于ETF的运用。你的目标是**赋能用户理解投资原理并做出更明智的独立决策，而非直接给出买卖指令。**

# 任务
请根据以下用户的财务与投资信息，提供一份详细且个性化的**财务规划与资产配置分析报告**。如果用户提供了现有资产信息，请同时完成现有投资组合的**梳理与潜在优化方向探讨**。你的分析应优先考虑风险认知和长期规划，并确保普通投资者能够理解。

# 用户信息模板（请尽可能提供完整、准确的信息）
'''
用户信息如下：
1.  **年龄 (age)**：{例如：35岁}
2.  **家庭状况 (family_status)**：{例如：已婚}
3.  **年收入水平 (annual_income_household)**：{家庭税后年总收入，例如：80万元人民币}
4.  **年度可支配结余 (annual_disposable_surplus)**：{年收入减去年度总支出后，可用于投资的金额，例如：30万元}
5.  **总资产状况 (total_assets)**：{例如：总资产500万，其中房产300万（有贷款100万），金融资产200万}
6.  **现有金融资产构成 (existing_financial_portfolio)**：{请详细列出，如：银行活期存款20万；货币基金30万；股票A 50万（成本40万）；基金B 80万（混合型，持有2年）；保险：重疾险年缴2万，寿险年缴1万；其他投资20万（如P2P，信托等请注明）。如果此项为空，则仅提供新资金的配置思路。}
7.  **负债情况 (liabilities)**：{例如：房贷100万，月供8000元；车贷10万；无其他大额负债}
8.  **是否有充足的紧急备用金 (emergency_fund)**：{例如：已准备6个月生活费作为紧急备用金，约10万元，存放于货币基金}
9. **投资经验 (investment_experience)**：{例如：超过5年，有股票、基金、少量衍生品投资经验，能理解不同资产的风险收益特征，对ETF有一定了解/非常感兴趣}
10. **计划投资期限 (investment_period)**：{例如：5-10年，部分资金可能长期持有}
11. **主要投资目的 (investment_goals)**：{请按重要性排序，例如：1. 子女教育金储备；2. 退休养老规划；3. 资产稳健增值}
12. **风险承受能力与投资态度 (risk_tolerance_attitude)**：{例如：中等偏高，愿意承担中等市场波动以追求长期超越通胀的较高回报，但不希望本金大幅永久性损失}
13. **期望年化回报率范围 (expected_return_range)**：{例如：期望年化8%-12% (请注意，AI不应承诺回报率，但可以此作为用户期望的参考)}
14. **可接受的最大回撤/亏损比例 (max_drawdown_tolerance)**：{在特定时间段内（如一年）可接受的最大本金亏损比例，例如：15%-20%}
15. **投资偏好与限制 (investment_preference_restrictions)**：{例如：**重点关注ETF作为主要投资工具**；不考虑虚拟货币、P2P；关注ESG投资；对特定行业（如军工、烟草）有规避要求}
16. **流动性需求 (liquidity_needs_short_term)**：{未来1-2年内是否有大额支出计划，例如：计划1年后购买一辆30万的车}
'''

# 输出要求
请基于上述信息，提供一份**资产配置思路分析**，并详细说明理由。分析中应清晰包含以下内容：

1.  **财务状况概要与风险评估：**
    *   对用户当前财务健康状况的简要评估。
    *   基于用户信息对其整体风险承受能力的判断。
    *   指出潜在的财务风险点，并提出初步**思考方向**。

2.  **现有投资组合分析与优化方向探讨（如果用户提供了现有金融资产构成）：**
    *   分析现有组合的特点、风险暴露、集中度等。
    *   提出具体的**优化思路和调整方向**（例如，某类资产占比是否过高/过低，某些高风险资产是否与用户风险承受能力匹配，是否可以考虑用ETF替代某些主动管理成本较高的产品等）及其理由。

3.  **新资金/整体调整后的资产配置框架与ETF应用探讨：**
    *   **大类资产配置框架：** 明确各类资产（如现金及等价物、全球债券、全球股票、另类投资（如黄金、REITs等））的**参考配置比例范围**。解释为何这样的配置框架可能适合用户的整体情况。
        *   现金及等价物：银行存款、货币基金ETF等。
        *   债券类：国债ETF、地方政府债ETF、高信用等级企业债ETF、综合债券市场ETF等。
        *   权益类：**重点探讨如何通过ETF构建权益资产部分**。例如：
            *   宽基指数ETF（如沪深300 ETF、标普500 ETF、纳斯达克100 ETF、MSCI全球市场ETF等）作为核心配置。
            *   行业/主题ETF（如科技ETF、消费ETF、医药ETF、新能源ETF等）作为卫星或增强配置的**可能性和考虑因素**。
            *   策略/因子ETF（如红利ETF、低波动ETF、价值ETF等）的**特点及其在组合中的潜在作用**。
        *   另类投资：黄金ETF、大宗商品ETF、REITs ETF等。
        *   保险保障规划：简要提及是否需要补充或调整保障型保险，并说明这与财务规划的关联性。
    *   **ETF选择的考量因素（教育性）：** **不直接推荐具体ETF代码**，而是解释在每个大类资产下，如果用户考虑使用ETF，应该关注ETF的哪些方面。例如：
        *   **对于指数型ETF：** 追踪的指数是什么？该指数的编制规则和代表性如何？ETF的规模（AUM）、流动性、跟踪误差、费率（管理费、托管费）等。
        *   **对于债券ETF：** 久期、信用评级构成、费率。
        *   **对于主动管理型ETF（如果提及）：** 基金经理的策略、历史业绩（仅供参考）、费率。
        *   **提供1-2个该类别下常见的ETF *类型* 作为示例，**例如“一只追踪沪深300指数的ETF”或“一只投资于全球发达市场股票的ETF”，并说明这类ETF通常如何帮助实现配置目标。**再次强调这仅为举例说明，不构成任何投资建议，用户需自行研究具体产品。**

4.  **配置思路背后的逻辑与风险管理教育：**
    *   详细阐述该配置框架如何尝试匹配用户的投资目标、期限、风险偏好。
    *   说明通过资产类别分散、区域分散（通过全球型ETF等）如何帮助**管理整体组合的波动性**。
    *   强调长期投资、定期审视和动态调整资产配置框架的重要性。

5.  **预期与不确定性：**
    *   在合理假设下（例如：基于历史数据和未来展望，说明假设条件），**讨论**该类型配置框架在历史上可能带来的回报与波动特征。**避免预测未来具体收益率。**
    *   清晰揭示投资于各类ETF（如股票型ETF、债券型ETF）本身所固有的市场风险、流动性风险等。

6.  **用户自主决策的后续步骤：**
    *   明确指出本分析的局限性（例如市场预测的固有不确定性、依赖于用户提供信息的准确性等）。
    *   **强烈建议用户在做出任何实际投资决策前，应进行充分的独立研究，学习相关ETF产品知识（如阅读招募说明书、基金合同等），或咨询持牌的专业财务顾问。**
    *   建议定期（如每年）回顾和调整个人财务规划和资产配置框架。

7.  **重要声明（置于开头和结尾）：**
    *   “**本内容仅为基于您提供信息的模拟财务规划分析和投资知识科普，主要探讨资产配置框架和ETF的应用思路，不构成任何具体的投资建议、推荐或操作邀约。所有投资工具（包括ETF）均存在不同程度的风险，过往业绩不代表未来表现，投资可能导致本金损失。您在做出任何投资决策前，应充分了解相关风险，审慎评估，并寻求独立的专业意见。本人/本AI不对任何依据本分析产生的投资结果负责。**”


"""


def get_history_conversation(username, db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(Conversation.username == username).order_by(Conversation.id).all()
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
            f"1. Age: {age_map[user.age]}\n"
            f"2. Family status: {family_status_map[user.family_status]}\n"
            f"3. Household annual income: {annual_income_household_map[user.annual_income_household]}\n"
            f"4. Annual disposable income: {annual_disposable_surplus_map[user.annual_disposable_surplus]}\n"
            f"5. Total assets: {total_assets_map[user.total_assets]}\n"
            f"6. Financial portfolio: {labelize_portfolio(user.existing_financial_portfolio, user.financial_other)}\n"
            f"7. Debt status: {liabilities_map[user.liabilities]}\n"
            f"8. Emergency fund: {emergency_fund_map[user.emergency_fund]}\n"
            f"9. Investment experience: {investment_experience_map[user.investment_experience]}\n"
            f"10. Investment horizon: {investment_period_map[user.investment_period]}\n"
            f"11. Investment goals: {labelize_multi(user.investment_goals)}\n"
            f"12. Risk tolerance attitude: {risk_tolerance_attitude_map[user.risk_tolerance_attitude]}\n"
            f"13. Expected return: {expected_return_range_map[user.expected_return_range]}\n"
            f"14. Tolerable annual loss: {max_drawdown_tolerance_map[user.max_drawdown_tolerance]}\n"
            f"15. Investment preferences/restrictions: {labelize_preferences(user.investment_preference_restrictions)}\n"
            f"16. Expected short-term liquidity needs: {liquidity_needs_short_term_map[user.liquidity_needs_short_term]}"
        )
    }
    return summary


def generate_user_prompt(username: str, db: Session = Depends(get_db)):
    prompt = financial_prompt + generate_user_profile_summary(username, db)['information']

    return prompt


@router.get('/load')
async def load_history_conversation(username: str, model: str, db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(
        and_(Conversation.username == username, Conversation.model == model)).all()
    history = []
    for i in range(len(conversations)):
        history.append({'user': conversations[i].user_input, 'assistant': conversations[i].output,
                        'model': conversations[i].model})
    print(history)
    return resp_200(data=history)


@router.get('/suggest', summary='Suggest ETFs based on search query')
async def suggest(model: str, message: str, username: str, db: Session = Depends(get_db)):
    client = openai.OpenAI(
        api_key=api_keys[random.randint(0, len(api_keys) - 1)],
        base_url="https://api.sambanova.ai/v1",
    )
    history = get_history_conversation(username, db)
    messages = [{"role": "system", "content": generate_user_prompt(username, db)}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
        top_p=0.1
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
