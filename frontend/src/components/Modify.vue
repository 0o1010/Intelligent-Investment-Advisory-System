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
                <el-form-item label="1. Your age falls into which of the following categories?" prop="age">
                    <el-radio-group v-model="registerForm.age">
                        <el-radio label="0">A. Below 25</el-radio>
                        <el-radio label="1">B. 25–35</el-radio>
                        <el-radio label="2">C. 36–45</el-radio>
                        <el-radio label="3">D. 46–55</el-radio>
                        <el-radio label="4">E. Above 55</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="2. What is your current family status?" prop="family_status">
                    <el-radio-group v-model="registerForm.family_status">
                        <el-radio label="0">A. Single</el-radio>
                        <el-radio label="1">B. Married without children</el-radio>
                        <el-radio label="2">C. Married with children</el-radio>
                        <el-radio label="3">D. Divorced</el-radio>
                        <el-radio label="4">E. Widowed</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="3. What is your household’s annual after-tax income?"
                              prop="annual_income_household">
                    <el-radio-group v-model="registerForm.annual_income_household">
                        <el-radio label="0">A. Below ¥200,000</el-radio>
                        <el-radio label="1">B. ¥200,000 – ¥500,000</el-radio>
                        <el-radio label="2">C. ¥500,000 – ¥1,000,000</el-radio>
                        <el-radio label="3">D. ¥1,000,000 – ¥2,000,000</el-radio>
                        <el-radio label="4">E. Over ¥2,000,000</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="4. How much disposable income do you have for investment each year?"
                              prop="annual_disposable_surplus">
                    <el-radio-group v-model="registerForm.annual_disposable_surplus">
                        <el-radio label="0">A. Below ¥50,000</el-radio>
                        <el-radio label="1">B. ¥50,000 – ¥150,000</el-radio>
                        <el-radio label="2">C. ¥150,000 – ¥300,000</el-radio>
                        <el-radio label="3">D. ¥300,000 – ¥500,000</el-radio>
                        <el-radio label="4">E. Over ¥500,000</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="5. What is the estimated value of your total assets?" prop="total_assets">
                    <el-radio-group v-model="registerForm.total_assets">
                        <el-radio label="0">A. Below ¥500,000</el-radio>
                        <el-radio label="1">B. ¥500,000 – ¥1,000,000</el-radio>
                        <el-radio label="2">C. ¥1,000,000 – ¥3,000,000</el-radio>
                        <el-radio label="3">D. ¥3,000,000 – ¥5,000,000</el-radio>
                        <el-radio label="4">E. Over ¥5,000,000</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="6. Which of the following assets are part of your current financial portfolio?"
                              prop="existing_financial_portfolio">
                    <el-checkbox-group
                        v-model="registerForm.existing_financial_portfolio"
                        @change="handleAssetChange">
                        <el-checkbox label="A">A. Bank savings</el-checkbox>
                        <el-checkbox label="B">B. Money market funds</el-checkbox>
                        <el-checkbox label="C">C. Mutual funds / ETFs</el-checkbox>
                        <el-checkbox label="D">D. Stocks</el-checkbox>
                        <el-checkbox label="E">E. Insurance</el-checkbox>
                        <el-checkbox label="F">F. Other</el-checkbox>
                        <el-input
                            v-if="registerForm.existing_financial_portfolio.includes('F')"
                            v-model="existingFinancialOther"
                            placeholder="Please input your 'Other' assets"
                            :style="{marginTop: '3px'}"
                        />
                        <el-checkbox label="G">G. None</el-checkbox>
                    </el-checkbox-group>
                </el-form-item>


                <el-form-item label="7. What is your current debt status?" prop="liabilities">
                    <el-radio-group v-model="registerForm.liabilities">
                        <el-radio label="0">A. No liabilities</el-radio>
                        <el-radio label="1">B. Minor debts</el-radio>
                        <el-radio label="2">C. Mortgage/car loan, manageable</el-radio>
                        <el-radio label="3">D. Large debts</el-radio>
                        <el-radio label="4">E. Heavily indebted</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="8. Do you have emergency savings equivalent to 6–12 months of living expenses?"
                              prop="emergency_fund">
                    <el-radio-group v-model="registerForm.emergency_fund">
                        <el-radio label="0">A. None</el-radio>
                        <el-radio label="1">B. Less than 3 months</el-radio>
                        <el-radio label="2">C. 3–6 months</el-radio>
                        <el-radio label="3">D. 6–12 months</el-radio>
                        <el-radio label="4">E. More than 12 months</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="9. How would you describe your investment experience?"
                              prop="investment_experience">
                    <el-radio-group v-model="registerForm.investment_experience">
                        <el-radio label="0">A. None</el-radio>
                        <el-radio label="1">B. Basic</el-radio>
                        <el-radio label="2">C. Moderate</el-radio>
                        <el-radio label="3">D. Advanced</el-radio>
                        <el-radio label="4">E. Professional</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="10. What is your intended investment horizon?" prop="investment_period">
                    <el-radio-group v-model="registerForm.investment_period">
                        <el-radio label="0">A. Less than 1 year</el-radio>
                        <el-radio label="1">B. 1–3 years</el-radio>
                        <el-radio label="2">C. 3–5 years</el-radio>
                        <el-radio label="3">D. 5–10 years</el-radio>
                        <el-radio label="4">E. Over 10 years</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="11. What are your primary investment goals?" prop="investment_goals">
                    <el-checkbox-group v-model="registerForm.investment_goals">
                        <el-checkbox label="A">A. Capital preservation</el-checkbox>
                        <el-checkbox label="B">B. Wealth accumulation</el-checkbox>
                        <el-checkbox label="C">C. Retirement planning</el-checkbox>
                        <el-checkbox label="D">D. Child education</el-checkbox>
                        <el-checkbox label="E">E. Short-term consumption</el-checkbox>
                    </el-checkbox-group>
                </el-form-item>

                <el-form-item label="12. How would you describe your attitude toward investment risk?"
                              prop="risk_tolerance_attitude">
                    <el-radio-group v-model="registerForm.risk_tolerance_attitude">
                        <el-radio label="0">A. Very conservative</el-radio>
                        <el-radio label="1">B. Conservative</el-radio>
                        <el-radio label="2">C. Moderate</el-radio>
                        <el-radio label="3">D. Aggressive</el-radio>
                        <el-radio label="4">E. Very aggressive</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="13. What is your expected annual return range?" prop="expected_return_range">
                    <el-radio-group v-model="registerForm.expected_return_range">
                        <el-radio label="0">A. Less than 4%</el-radio>
                        <el-radio label="1">B. 4% – 6%</el-radio>
                        <el-radio label="2">C. 6% – 8%</el-radio>
                        <el-radio label="3">D. 8% – 12%</el-radio>
                        <el-radio label="4">E. Over 12%</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="14. What level of loss can you tolerate in a single year?"
                              prop="max_drawdown_tolerance">
                    <el-radio-group v-model="registerForm.max_drawdown_tolerance">
                        <el-radio label="0">A. Less than 5%</el-radio>
                        <el-radio label="1">B. 5% – 10%</el-radio>
                        <el-radio label="2">C. 10% – 15%</el-radio>
                        <el-radio label="3">D. 15% – 20%</el-radio>
                        <el-radio label="4">E. Over 20%</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item label="15. Do you have any preferences or restrictions regarding investment instruments?"
                              prop="investment_preference_restrictions">
                    <el-checkbox-group v-model="registerForm.investment_preference_restrictions">
                        <el-checkbox label="A">A. Prefer ETFs as core allocation</el-checkbox>
                        <el-checkbox label="B">B. Avoid crypto/P2P/high risk</el-checkbox>
                        <el-checkbox label="C">C. Prefer ESG investments</el-checkbox>
                        <el-checkbox label="D">D. Avoid specific sectors</el-checkbox>
                        <el-checkbox label="E">E. No restrictions</el-checkbox>
                    </el-checkbox-group>
                </el-form-item>

                <el-form-item label="16. Do you expect any major spending in the next 1–2 years?"
                              prop="liquidity_needs_short_term">
                    <el-radio-group v-model="registerForm.liquidity_needs_short_term">
                        <el-radio label="0">A. No</el-radio>
                        <el-radio label="1">B. Yes, within ¥100,000</el-radio>
                        <el-radio label="2">C. ¥100,000 – ¥300,000</el-radio>
                        <el-radio label="3">D. ¥300,000 – ¥500,000</el-radio>
                        <el-radio label="4">E. Over ¥500,000</el-radio>
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
                age: '',
                family_status: '',
                annual_income_household: '',
                annual_disposable_surplus: '',
                total_assets: '',
                existing_financial_portfolio: [],
                liabilities: '',
                emergency_fund: '',
                investment_experience: '',
                investment_period: '',
                investment_goals: [],
                risk_tolerance_attitude: '',
                expected_return_range: '',
                max_drawdown_tolerance: '',
                investment_preference_restrictions: [],
                liquidity_needs_short_term: '',
            },
            existingFinancialOther: "",
        };
    },
    beforeMount() {
        this.fetchUserInfo();
    },
    computed: {
        hasOtherAssets() {
            return this.registerForm.existing_financial_portfolio.some(opt => opt !== 'G');
        }
    },
    methods: {
        handleAssetChange(val) {
            if (val[val.length - 1] === 'G') {
                this.registerForm.existing_financial_portfolio = ['G'];
                this.existingFinancialOther = '';
            } else {
                const index = val.indexOf('G');
                if (index !== -1) {
                    val.splice(index, 1);
                }
                if (!val.includes('F')) {
                    this.existingFinancialOther = '';
                }

                this.registerForm.existing_financial_portfolio = [...val];
            }
        },
        fetchUserInfo() {
            this.$axios.get(this.$httpUrl + '/info', {
                params: {
                    username: sessionStorage.getItem('user')
                }
            }).then(res => res.data).then(res => {
                if (res.data) {
                    const data = res.data;
                    Object.keys(this.registerForm).forEach(key => {
                        this.registerForm[key] = Array.isArray(this.registerForm[key])
                            ? data[key] || []
                            : String(data[key]);
                    });
                    this.existingFinancialOther = String(res.data.financial_other)
                }
            });
        },

        submitForm() {
            if (this.registerForm.existing_financial_portfolio.includes('F') &&
                !this.existingFinancialOther.trim()) {
                this.$message.error("Please specify your 'Other' asset details");
                return;
            }
            this.$axios.post(this.$httpUrl + '/update', {
                ...this.registerForm,
                financial_other: this.existingFinancialOther
            }).then(res => res.data).then(res => {
                if (res.data) {
                    this.$message.success('Modify successfully');
                } else {
                    this.$message.error('Modify failed');
                }
            }).catch(() => {
                this.$message.error('Request failed');
            });
        },
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
