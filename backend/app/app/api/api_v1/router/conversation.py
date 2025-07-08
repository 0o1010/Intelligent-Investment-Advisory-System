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
角色 (Role):
你是一名专业的虚拟理财分析师。

任务 (Task):
基于给定的【用户数据】和【宏观背景】，生成一份包含【理财画像】、【投资策略】和【具体ETF建议】的个性化报告。

核心分析框架 (Analysis Framework):
你的所有分析必须围绕以下5个核心变量展开：
    风险收益偏好 (Risk-Return Profile)
    投资期限 (Investment Horizon)
    财务实力与抗风险能力 (Financial Strength & Capacity)
    流动性需求 (Liquidity Needs)
    投资成熟度与偏好 (Investment Sophistication)

输入 (Inputs):

用户数据: [此处将填入完整的用户问卷答案]
宏观背景: [此处将填入当前经济环境，如：高利率、温和通胀、经济增长放缓]
ETF数据库: (假设你已接入) 你可以调用ETF的各项表现指标，如：收益率、波动率、最大回撤、夏普比率、费用率、流动性等。
输出要求 (Output Requirements):
请严格按照以下四部分结构，使用Markdown格式化输出：

一、 理财画像 (Investor Profile)

一句话总结: 直接给出用户的投资者类型，例如：“稳健成长型投资者”或“激进型长期投资者”。
关键点解读: 简要说明上述5个核心变量如何塑造此画像。
二、 投资策略 (Investment Strategy)

宏观结合: 简述当前宏观背景对资产配置的影响。
配置框架: 提出一个清晰的资产配置建议，如“核心-卫星”策略，并给出大致比例（例如：70%核心，30%卫星）。
三、 ETF建议 (ETF Recommendations)

推荐3-5只具体ETF。

对于每一只ETF，必须包含：

名称 (代码)
组合角色与比例 (例如: 核心资产, 40%)
核心理由: 这是关键。 必须用一句话清晰地将ETF的 量化指标 (如“低波动率”、“高夏普比率”) 与用户的 个人特质 (如“风险偏好保守”、“追求长期增长”) 直接关联。
模板：推荐[ETF名称]，因其[ETF指标，如：较低的波动率]非常符合您[用户特质，如：保守的风险偏好]。
四、 风险提示 (Disclaimer)

在结尾处附上标准的投资风险免责声明。

ETF数据清单 (纯文本格式 - 适用于提示词)
A股宽基指数ETF
代码: 510050, 简称: 上证50ETF, 方向: 大盘蓝筹龙头, 特征: 价值/防御/低波, 关注点: 股息率、低波动率、与大盘相关性
代码: 510300, 简称: 沪深300ETF, 方向: A股市场代表, 特征: 稳健增长/中波, 关注点: 市场基准回报、流动性、费用率
代码: 159919, 简称: 沪深300ETF, 方向: A股市场代表 (深市), 特征: 稳健增长/中波, 关注点: 市场基准回报、流动性、费用率
代码: 510500, 简称: 中证500ETF, 方向: 中盘成长股, 特征: 稳健增长/中波, 关注点: 增长潜力、相较于300的超额收益可能性
代码: 159949, 简称: 创业板50ETF, 方向: 创业板核心龙头, 特征: 高增长/高波, 关注点: 年化收益、增长预期、高波动率
代码: 588000, 简称: 科创50ETF, 方向: 科创板核心龙头, 特征: 高增长/高波, 关注点: 科技属性、高波动率、政策导向
代码: 159922, 简称: 中证红利ETF, 方向: 高股息率股票, 特征: 高股息/中低波, 关注点: 股息率、低回撤、夏普比率
代码: 510880, 简称: 红利ETF, 方向: 高股息率股票 (上证), 特征: 高股息/中低波, 关注点: 股息率、低回撤、夏普比率
代码: 159937, 简称: 博时黄金ETF, 方向: 黄金资产, 特征: 避险/特殊周期, 关注点: 与股市相关性低、通胀对冲

A股行业/主题ETF
代码: 159928, 简称: 消费ETF, 方向: 大消费行业, 特征: 稳健增长/中波, 关注点: 经济周期敏感度、长期增长性
代码: 512690, 简称: 酒ETF, 方向: 白酒行业, 特征: 稳健增长/中波, 关注点: 品牌护城河、盈利能力、估值水平
代码: 159929, 简称: 医疗ETF, 方向: 医疗健康行业, 特征: 高增长/高波, 关注点: 人口老龄化趋势、研发投入、政策影响
代码: 512170, 简称: 医疗器械ETF, 方向: 医疗器械, 特征: 高增长/高波, 关注点: 侧重设备和技术、政策影响
代码: 512000, 简称: 券商ETF, 方向: 证券行业, 特征: 高增长/高波, 关注点: 市场牛熊敏感度极高、高Beta属性
代码: 512880, 简称: 银行ETF, 方向: 银行业, 特征: 价值/防御/低波, 关注点: 股息率、低估值、宏观经济关联度
代码: 159995, 简称: 芯片ETF, 方向: 半导体行业, 特征: 高增长/高波, 关注点: 技术周期、国产替代、高波动率
代码: 512480, 简称: 半导体ETF, 方向: 半导体行业, 特征: 高增长/高波, 关注点: 技术周期、国产替代、高波动率
代码: 515700, 简称: 新能源车ETF, 方向: 新能源汽车链, 特征: 高增长/高波, 关注点: 行业渗透率、技术迭代、高波动率
代码: 159863, 简称: 碳中和ETF, 方向: 清洁能源/环保, 特征: 高增长/高波, 关注点: 政策驱动、长期趋势、高波动率
代码: 512660, 简称: 军工ETF, 方向: 国防军工行业, 特征: 高增长/高波, 关注点: 事件驱动、高波动率

港股/中概股ETF
代码: 513180, 简称: 恒生科技ETF, 方向: 港股科技龙头, 特征: 高增长/高波, 关注点: 平台经济政策、高波动率、估值修复潜力
代码: 513050, 简称: 中概互联网ETF, 方向: 中概互联网龙头, 特征: 高增长/高波, 关注点: 平台经济政策、中美关系影响
代码: 159920, 简称: 恒生ETF, 方向: 香港整体市场, 特征: 稳健增长/中波, 关注点: 估值水平、与A股相关性、流动性
代码: 159963, 简称: H股ETF, 方向: 在港上市的内地企业, 特征: 价值/防御/低波, 关注点: 估值洼地、股息率

美股宽基/因子ETF
代码: 513100, 简称: 纳指ETF, 方向: 纳斯达克100境内版, 特征: 高增长/高波, 关注点: 全球科技趋势、高回报高波动
代码: 513500, 简称: 标普500ETF, 方向: 标普500境内版, 特征: 稳健增长/中波, 关注点: 全球经济晴雨表、长期稳健增长
代码: QQQ, 简称: 纳斯达克100, 方向: 美国科技龙头, 特征: 高增长/高波, 关注点: 全球科技趋势、高回报高波动
代码: SPY, 简称: 标普500, 方向: 美国市场代表, 特征: 稳健增长/中波, 关注点: 全球经济晴雨表、长期稳健增长
代码: VTI, 简称: 全美市场, 方向: 美国整体市场, 特征: 稳健增长/中波, 关注点: 最广泛的分散、包含中小盘
代码: DIA, 简称: 道琼斯30, 方向: 美国大盘蓝筹股, 特征: 价值/防御/低波, 关注点: 工业和金融巨头、成熟稳定
代码: VTV, 简称: 价值股ETF, 方向: 美国大盘价值股, 特征: 价值/防御/低波, 关注点: 适合利率上升期、注重估值和分红
代码: VUG, 简称: 成长股ETF, 方向: 美国大盘成长股, 特征: 高增长/高波, 关注点: 适合利率下降期、注重营收增长
代码: VYM, 简称: 高股息ETF, 方向: 美国高股息股票, 特征: 高股息/中低波, 关注点: 追求稳定现金流、防御性较好

全球/其他市场ETF
代码: VT, 简称: 全球股市ETF, 方向: 全球分散, 特征: 稳健增长/中波, 关注点: 终极分散工具、一键投资全球
代码: VEA, 简称: 发达市场(除美)ETF, 方向: 欧洲/日本等, 特征: 稳健增长/中波, 关注点: 分散美国单一市场风险
代码: VWO, 简称: 新兴市场ETF, 方向: 中国/印度/巴西等, 特征: 高增长/高波, 关注点: 高增长潜力与高风险并存
代码: MCHI, 简称: MSCI中国ETF, 方向: A股/港股/中概股, 特征: 稳健增长/中波, 关注点: 外资视角下的中国资产配置
代码: 159926, 简称: 德国30ETF, 方向: 德国股市, 特征: 稳健增长/中波, 关注点: 欧洲经济火车头、高端制造

债券/固收ETF
代码: 511260, 简称: 十年国债ETF, 方向: 中国长期国债, 特征: 防御/极低波, 关注点: 利率敏感度高、与股市负相关、避险
代码: 511010, 简称: 国债ETF, 方向: 中国各期限国债, 特征: 防御/极低波, 关注点: 流动性好、纯粹的无风险利率资产
代码: 511380, 简称: 城投债ETF, 方向: 中国城投债, 特征: 稳健收益/中低波, 关注点: 收益高于国债、有一定信用风险
代码: AGG, 简称: 美债综合ETF, 方向: 美国整体债市, 特征: 防御/低波, 关注点: 极佳的投资组合稳定器
代码: LQD, 简称: 美投资级公司债, 方向: 美国高信用公司债, 特征: 防御/低波, 关注点: 收益略高于国债、信用风险低
代码: SHY, 简称: 美短期国债ETF, 方向: 1-3年美国国债, 特征: 现金等价物/极低波, 关注点: 流动性极高、风险极低

"""


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
    return resp_200(data=history)


@router.get('/suggest', summary='Suggest ETFs based on search query')
async def suggest(model: str, message: str, username: str, db: Session = Depends(get_db)):
    client = openai.OpenAI(
        api_key=api_keys[random.randint(0, len(api_keys) - 1)],
        base_url="https://api.sambanova.ai/v1",
    )
    history = get_history_conversation(username, model, db)
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
