import random

from fastapi import APIRouter, Depends
import openai
from sqlalchemy.orm import Session
from app.db.db_session import get_db
from app.models.conversation import Conversation
from app.models.user import User
from app.core.response import resp_200, resp_401

router = APIRouter()

api_keys = ['f1cbcbfc-b023-4743-b959-47a625a8852f', '7bd2d286-06d5-494d-9b8a-e6492add377e',
            'd055fb6c-0c4e-4e7d-8ddb-447bdb19d6e4', 'b83ced09-7a1d-4e4d-94eb-7434d8afe798']

financial_prompt = """
你是一位专业的金融投资顾问，具有丰富的财富管理经验。现在，请你根据以下用户的财务与投资信息，提供个性化的投资组合建议（可包括股票、基金、债券、保险、存款等），你还需要根据现有资产完成投资组合优化。
下面我将给你一个仅供参考的例子来说明用户信息。
'''
用户信息如下：
1. 当前财务状况（financial_status）：{例如：有相当多的储蓄并有一定投资}
2. 家庭总资产中计划投资的比例（assets_percentage）：{例如：10-20%}
3. 年收入水平（annual_income）：{例如：20万 - 50万}
4. 投资经验（investment_experience）：{例如：有基金、股票投资经验}
5. 计划投资期限（investment_period）：{例如：3-5年}
6. 投资目的（investment_goal）：{例如：资产增值}
7. 投资态度（investment_attitude）：{例如：愿意承担一定波动追求较高收益}
8. 投资偏好（investment_preference）：{例如：30%收益但可能有15%亏损}
9. 可接受的最大投资亏损（risk_tolerance）：{例如：可接受最大亏损为30%-50%}
'''
请基于这些信息推荐一个资产配置方案，并说明理由。建议中应包括：
- 每类资产（如股票、债券、基金、黄金、现金等）的配置比例；
- 投资建议背后的逻辑与风险控制策略；
- 不确定之处请指出并解释；
- 不得编造数据来源，如需假设某种市场情况，请说明“在某种假设下”。

请用清晰、简明的语言进行回答，适合普通投资者理解。

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
    q1_map = [
        "Significant amount of outstanding liabilities",
        "Offsetting of income and expenditure",
        "Have some savings",
        "Have relatively large savings and some investment",
        "Wealthier and with considerable investment"
    ]
    q2_map = [
        "80-100%",
        "50-80%",
        "20-50%",
        "10-20%",
        "0-10%"
    ]
    q3_map = [
        "Less than $200,000",
        "$200,000 to $500,000",
        "$500,000 to $1,500,000",
        "$1.5 million to $5 million",
        "More than $5 million"
    ]
    q4_map = [
        "Basically no investment experience other than bank savings",
        "Have purchased bank financial products",
        "Have purchased bonds, insurance and other financial products",
        "Participated in the trading of stocks, funds and others",
        "Participated in the trading of warrants, futures, options and others"
    ]
    q5_map = [
        "Less than 1 year",
        "1-2 years",
        "2-3 years",
        "3-5 years",
        "More than 5 years"
    ]
    q6_map = [
        "Usual livelihood security, earn a little to subsidize the household",
        "Elderly care",
        "Education of children",
        "Asset enhancement",
        "Enrich families"
    ]
    q7_map = [
        "Prioritizes capital preservation with guaranteed stable returns",
        "Accepts minor yield fluctuations but requires full principal protection",
        "Targets controlled growth through calculated, low-to-medium risks",
        "Pursues higher returns with limited principal volatility tolerance",
        "Seeks maximum returns while embracing significant capital loss risks"
    ]
    q8_map = [
        "Gains of only 5%, but no losses",
        "15% gain but possible 5% loss",
        "The gain is 30%, but the loss may be 15%",
        "50% gain but possible 30% loss",
        "100% gain but possible 60% loss"
    ]
    q9_map = [
        "Less than 10%",
        "10%－20%",
        "20%－30%",
        "30%－50%",
        "More than 50%"
    ]

    summary = {'information':
                   f"My current personal and family financial situation: {q1_map[user.financial_status]}.\n"
                   f"The proportion of the amount of funds I have invested or intend to invest in to the total assets owned by me or my family: {q2_map[user.assets_percentage]}.\n"
                   f"My annual income: {q3_map[user.annual_income]}.\n"
                   f"My investment experience: {q4_map[user.investment_experience]}.\n"
                   f"The duration of my planned investment: {q5_map[user.investment_period]}.\n"
                   f"My main purposes of investing in fund accounts, brokerage plans, trust plans and other products: {q6_map[user.investment_goal]}.\n"
                   f"My investment attitude: {q7_map[user.investment_attitude]}.\n"
                   f"My investment preference: {q8_map[user.investment_preference]}.\n"
                   f"The maximum investment loss I can afford: {q9_map[user.risk_tolerance]}."
               }
    return summary

def generate_user_prompt(username: str, db: Session=Depends(get_db)):
    prompt = financial_prompt + generate_user_profile_summary(username, db)['information']

    return prompt

@router.get('/load')
async def load_history_conversation(username: str, db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(Conversation.username == username).all()
    history = []
    for i in range(len(conversations)):
        history.append({'user': conversations[i].user_input, 'assistant': conversations[i].output})
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
        output=output
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return resp_200(data=response.choices[0].message.content)
