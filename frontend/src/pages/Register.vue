<template>
    <div class="login-container">
        <el-form ref="registerForm" :model="registerForm" :rules="registerRules" class="login-form" auto-complete="on"
                 label-position="left">
            <div class="title-container">
                <h3 class="title">User Register</h3>
            </div>

            <el-form-item prop="username">
                <span class="svg-container">
                    <i class="el-icon-user"/>
                </span>
                <el-input
                    ref="username"
                    v-model="registerForm.username"
                    placeholder="Input username"
                    name="username"
                    type="text"
                    auto-complete="on"
                />
            </el-form-item>

            <el-form-item prop="password">
                <span class="svg-container">
                    <i class="el-icon-lock"/>
                </span>
                <el-input
                    placeholder="Input password"
                    v-model="registerForm.password"
                    show-password
                />
            </el-form-item>

            <el-form-item prop="repassword">
                <span class="svg-container">
                    <i class="el-icon-lock"/>
                </span>
                <el-input
                    placeholder="Input password again"
                    v-model="registerForm.repassword"
                    show-password
                />
            </el-form-item>

            <el-divider>Financial Questionnaire</el-divider>

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

            <el-form-item label="3. What is your household’s annual after-tax income?" prop="annual_income_household">
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

            <el-form-item label="9. How would you describe your investment experience?" prop="investment_experience">
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


            <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 30px;">
                <el-button :loading="loading" type="primary" style="width: 50%;"
                           @click.native.prevent="handleRegister">Register
                </el-button>
                <el-button :loading="loading" type="success" style="width: 50%;"
                           @click.native.prevent="back">Back
                </el-button>
            </div>

        </el-form>
    </div>
</template>

<script>
export default {
    name: "Register",
    data() {
        const validatePassword = (rule, value, callback) => {
            if (value.length < 6) {
                callback(new Error('Password cannot be less than 6 digits'))
            } else {
                callback()
            }
        };
        const validateRepassword = (rule, value, callback) => {
            if (value !== this.registerForm.password) {
                callback(new Error('Passwords do not match'))
            } else {
                callback()
            }
        };

        return {
            registerForm: {
                username: '',
                password: '',
                repassword: '',
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
            registerRules: {
                username: [
                    {required: true, message: 'Input username', trigger: 'blur'},
                    {min: 3, max: 20, message: '3 to 20 characters in length', trigger: 'blur'}
                ],
                password: [
                    {required: true, validator: validatePassword, trigger: 'blur'}
                ],
                repassword: [
                    {required: true, validator: validateRepassword, trigger: 'blur'}
                ],
                age: [{required: true, message: 'Please select your age group', trigger: 'change'}],
                family_status: [{required: true, message: 'Please select your family status', trigger: 'change'}],
                annual_income_household: [{required: true, message: 'Please select income range', trigger: 'change'}],
                annual_disposable_surplus: [{
                    required: true,
                    message: 'Please select surplus amount',
                    trigger: 'change'
                }],
                total_assets: [{required: true, message: 'Please select asset range', trigger: 'change'}],
                existing_financial_portfolio: [{
                    required: true,
                    type: 'array',
                    min: 1,
                    message: 'Select at least one portfolio',
                    trigger: 'change'
                }],
                liabilities: [{required: true, message: 'Please select debt status', trigger: 'change'}],
                emergency_fund: [{required: true, message: 'Please select emergency fund status', trigger: 'change'}],
                investment_experience: [{
                    required: true,
                    message: 'Please select investment experience',
                    trigger: 'change'
                }],
                investment_period: [{required: true, message: 'Please select investment period', trigger: 'change'}],
                investment_goals: [{
                    required: true,
                    type: 'array',
                    min: 1,
                    message: 'Select at least one goal',
                    trigger: 'change'
                }],
                risk_tolerance_attitude: [{required: true, message: 'Please select risk attitude', trigger: 'change'}],
                expected_return_range: [{required: true, message: 'Please select expected return', trigger: 'change'}],
                max_drawdown_tolerance: [{required: true, message: 'Please select tolerance', trigger: 'change'}],
                investment_preference_restrictions: [{
                    required: true,
                    type: 'array',
                    min: 1,
                    message: 'Select at least one preference',
                    trigger: 'change'
                }],
                liquidity_needs_short_term: [{
                    required: true,
                    message: 'Please select liquidity need',
                    trigger: 'change'
                }],
            },
            loading: false
        }
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
        handleRegister() {
            this.$refs.registerForm.validate(valid => {
                if (valid) {
                    if (this.registerForm.existing_financial_portfolio.includes('F') &&
                        !this.existingFinancialOther.trim()) {
                        this.$message.error("Please specify your 'Other' asset details");
                        return;
                    }

                    this.loading = true;
                    this.$axios.post(this.$httpUrl + '/register', {
                        ...this.registerForm,
                        financial_other: this.existingFinancialOther
                    }).then(res => {
                        if (res.data.code === 200) {
                            this.$message.success('Register successfully');
                            sessionStorage.setItem('user', res.data.data)
                            this.$router.replace('/index')
                        } else {
                            this.$message.error(res.data.msg);
                        }
                    }).catch(error => {
                        this.$message.error('Register failed');
                        console.error(error);
                    }).finally(() => {
                        this.loading = false;
                    });
                }
            });
        },

        back() {
            this.$router.go(-1)
        },
    }
}
</script>

<style lang="scss">

$bg: #283443;
$light_gray: #fff;
$cursor: #fff;

@supports (-webkit-mask: none) and (not (cater-color: $cursor)) {
    .login-container .el-input input {
        color: $cursor;
    }
}

/* reset element-ui css */
.login-container {
    .el-input {
        display: inline-block;
        height: 47px;
        width: 89%;

        input {
            background: transparent;
            border: 0px;
            -webkit-appearance: none;
            border-radius: 0px;
            padding: 12px 5px 12px 15px;
            color: $light_gray;
            height: 47px;
            caret-color: $cursor;

            &:-webkit-autofill {
                box-shadow: 0 0 0px 1000px $bg inset !important;
                -webkit-text-fill-color: $cursor !important;
            }
        }
    }


    .el-form-item {
        border: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(0, 0, 0, 0.1);
        border-radius: 5px;
        color: #454545;

        label {
            margin-left: 10px;
            color: $light_gray !important;
        }
    }
}
</style>

<style lang="scss" scoped>
$bg: #2d3a4b;
$dark_gray: #889aa4;
$light_gray: #eee;

.login-container {
    //width: 100%;
    //height: 100%;
    background-color: #2d3a4b;
    overflow: hidden;

    .login-form {
        position: relative;
        width: 520px;
        max-width: 100%;
        padding: 160px 35px 0;
        margin: 0 auto;
        overflow: hidden;
    }

    .svg-container {
        padding: 6px 5px 6px 15px;
        color: $dark_gray;
        vertical-align: middle;
        width: 15px;
        display: inline-block;
    }

    .title-container {
        position: relative;

        .title {
            font-size: 26px;
            color: $light_gray;
            margin: 0px auto 40px auto;
            text-align: center;
            font-weight: bold;
        }
    }

    .el-radio {
        color: $light_gray !important;
        margin: 10px 10px;
    }
}
</style>

