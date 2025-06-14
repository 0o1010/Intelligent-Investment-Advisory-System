<template>
    <div class="edit-user-info">
        <el-card class="box-card">
            <h2 class="title">Modify Personal Financial Information</h2>
            <el-form ref="registerForm" :model="registerForm" auto-complete="on"
                     label-position="left">
                <el-form-item prop="username">
                    <el-input
                        v-model="registerForm.username"
                        :disabled="true"
                    />

                </el-form-item>
                <el-form-item
                    label="1. Your current personal and family financial situation falls into which of the following categories:"
                    prop="q1">

                    <el-radio-group v-model="registerForm.financial_status">
                        <el-radio label="0">A. Significant amount of outstanding liabilities</el-radio>
                        <el-radio label="1">B. Offsetting of income and expenditure</el-radio>
                        <el-radio label="2">C. Have some savings</el-radio>
                        <el-radio label="3">D. Have relatively large savings and some investment</el-radio>
                        <el-radio label="4">E. Wealthier and with considerable investment</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item
                    label="2. What is the proportion of the amount of funds you have invested or intend to invest in to the total assets owned by you or your family: (Remarks: Total assets include deposits, securities investment, real estate and industry, etc.)"
                    prop="q2">
                    <el-radio-group v-model="registerForm.assets_percentage">
                        <el-radio label="0">A. 80-100%</el-radio>
                        <el-radio label="1">B. 50-80%</el-radio>
                        <el-radio label="2">C. 20-50%</el-radio>
                        <el-radio label="3">D. 10-20%</el-radio>
                        <el-radio label="4">E. 0-10%</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="3. What is your annual income:" prop="q3">
                    <el-radio-group v-model="registerForm.annual_income">
                        <el-radio label="0">A. Less than $200,000</el-radio>
                        <el-radio label="1">B. $200,000 to $500,000</el-radio>
                        <el-radio label="2">C. $500,000 to $1,500,000</el-radio>
                        <el-radio label="3">D. $1.5 million to $5 million</el-radio>
                        <el-radio label="4">E. More than $5 million</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="4. Your investment experience can be described as:" prop="q4">
                    <el-radio-group v-model="registerForm.investment_experience">
                        <el-radio label="0">A. Basically no investment experience other than bank savings
                        </el-radio>
                        <el-radio label="1">B. Have purchased bank financial products</el-radio>
                        <el-radio label="2">C. Have purchased bonds, insurance and other financial products</el-radio>
                        <el-radio label="3">D. Participated in the trading of stocks, funds and others</el-radio>
                        <el-radio label="4">E. Participated in the trading of warrants, futures, options and others
                        </el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="5. What is the duration of your planned investment:" prop="q5">
                    <el-radio-group v-model="registerForm.investment_period">
                        <el-radio label="0">A. Less than 1 year</el-radio>
                        <el-radio label="1">B. 1-2 years</el-radio>
                        <el-radio label="2">C. 2-3 years</el-radio>
                        <el-radio label="3">D. 3-5 years</el-radio>
                        <el-radio label="4">E. More than 5 years</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item
                    label="6. What are the main purposes for which you invest in fund accounts, brokerage plans, trust plans and other products:"
                    prop="q6">
                    <el-radio-group v-model="registerForm.investment_goal">
                        <el-radio label="0">A. Usual livelihood security, earn a little to subsidize the household
                        </el-radio>
                        <el-radio label="1">B. Elderly care</el-radio>
                        <el-radio label="2">C. Education of children</el-radio>
                        <el-radio label="3">D. Asset enhancement</el-radio>
                        <el-radio label="4">E. Enrich families</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item
                    label="7. Which of the following descriptions best matches your attitude toward investing:"
                    prop="q7">
                    <el-radio-group v-model="registerForm.investment_attitude">
                        <el-radio label="0">A. Prioritizes capital preservation with guaranteed stable returns
                        </el-radio>
                        <el-radio label="1">B. Accepts minor yield fluctuations but requires full principal protection
                        </el-radio>
                        <el-radio label="2">C. Targets controlled growth through calculated, low-to-medium risks
                        </el-radio>
                        <el-radio label="3">D. Pursues higher returns with limited principal volatility tolerance
                        </el-radio>
                        <el-radio label="4">E. Seeks maximum returns while embracing significant capital loss risks
                        </el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="8. Which of the following investment models do you prefer:" prop="q8">
                    <el-radio-group v-model="registerForm.investment_preference">
                        <el-radio label="0">A. Gains of only 5%, but no losses</el-radio>
                        <el-radio label="1">B. 15% gain but possible 5% loss</el-radio>
                        <el-radio label="2">C. The gain is 30%, but the loss may be 15%.</el-radio>
                        <el-radio label="3">D. 50% gain but possible 30% loss</el-radio>
                        <el-radio label="4">E. 100% gain but possible 60% loss</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="9. What is the maximum investment loss you think you can afford:" prop="q9">
                    <el-radio-group v-model="registerForm.risk_tolerance">
                        <el-radio label="0">A. Less than 10%</el-radio>
                        <el-radio label="1">B. 10%－20%</el-radio>
                        <el-radio label="2">C. 20%－30%</el-radio>
                        <el-radio label="3">D. 30%－50%</el-radio>
                        <el-radio label="4">E. More than 50%</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="submitForm">Submit</el-button>
                </el-form-item>
            </el-form>
        </el-card>
    </div>
</template>

<script>
export default {
    name: "Modify",
    data() {
        return {
            registerForm: {
                username: '',
                financial_status: '',
                assets_percentage: '',
                annual_income: '',
                investment_experience: '',
                investment_period: '',
                investment_goal: '',
                investment_attitude: '',
                investment_preference: '',
                risk_tolerance: '',
            },
        };
    },
    beforeMount() {
        this.fetchUserInfo();
    },
    methods: {
        fetchUserInfo() {
            this.$axios.get(this.$httpUrl + '/info', {
                params: {
                    username: sessionStorage.getItem('user')
                }
            }).then(res => res.data).then(res => {
                if (res.data) {
                    console.log(res.data.annual_income);
                    this.registerForm.username = res.data.username;
                    this.registerForm.annual_income = String(res.data.annual_income);
                    this.registerForm.financial_status = String(res.data.financial_status);
                    this.registerForm.assets_percentage = String(res.data.assets_percentage);
                    this.registerForm.investment_attitude = String(res.data.investment_attitude);
                    this.registerForm.investment_goal = String(res.data.investment_goal);
                    this.registerForm.investment_experience = String(res.data.investment_experience);
                    this.registerForm.investment_period = String(res.data.investment_period);
                    this.registerForm.investment_preference = String(res.data.investment_preference);
                    this.registerForm.risk_tolerance = String(res.data.risk_tolerance);

                }
            })
        },

        submitForm() {
            this.$axios.post(this.$httpUrl + '/update', this.registerForm).then(res => res.data).then(res => {
                if (res.data) {
                    this.$message.success('Modify successfully');
                } else {
                    this.$message.error('Modify failed');
                }
            }).catch(() => {
                this.$message.error('Request failed');
            });
            this.fetchUserInfo();
        }
    }
}
</script>
<style scoped>
.edit-user-info {
    max-width: 800px;
    margin: 0 auto;
    padding: 40px 30px;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    background-color: #fff;
}

.box-card {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    border-radius: 12px;
    padding: 40px;
}

.title {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 30px;
    color: #222;
    text-align: center;
}

.el-form-item {
    margin-bottom: 40px;
    align-items: flex-start;
}

.el-form-item__label {
    font-weight: 500;
    color: #333;
    line-height: 1.6;
    white-space: normal;
    width: 100%;
    text-align: left;
    font-size: 16px;
    margin-bottom: 10px;
}

.el-form-item__content {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.el-radio {
    font-size: 15px;
    color: #444;
}

.el-button {
    display: block;
    margin: 40px auto 0;
    padding: 12px 40px;
    font-size: 16px;
    border-radius: 8px;
}
</style>
