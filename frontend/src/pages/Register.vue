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

            <el-divider>Financial questionnaire</el-divider>

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
            <el-form-item label="7. Which of the following descriptions best matches your attitude toward investing:"
                          prop="q7">
                <el-radio-group v-model="registerForm.investment_attitude">
                    <el-radio label="0">A. Prioritizes capital preservation with guaranteed stable returns</el-radio>
                    <el-radio label="1">B. Accepts minor yield fluctuations but requires full principal protection
                    </el-radio>
                    <el-radio label="2">C. Targets controlled growth through calculated, low-to-medium risks</el-radio>
                    <el-radio label="3">D. Pursues higher returns with limited principal volatility tolerance</el-radio>
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
                callback(new Error('Inconsistency between two password entries'))
            } else {
                callback()
            }
        };

        return {
            registerForm: {
                username: '',
                password: '',
                repassword: '',
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
                financial_status: [
                    {required: true, message: 'Please select an answer', trigger: 'blur'},
                ],
                assets_percentage: [
                    {required: true, message: 'Please select an answer', trigger: 'blur'},
                ],
                annual_income: [
                    {required: true, message: 'Please select an answer', trigger: 'blur'},
                ],
                investment_experience: [
                    {required: true, message: 'Please select an answer', trigger: 'blur'},
                ],
                investment_period: [
                    {required: true, message: 'Please select an answer', trigger: 'blur'},
                ],
                investment_goal: [
                    {required: true, message: 'Please select an answer', trigger: 'blur'},
                ],
                investment_attitude: [
                    {required: true, message: 'Please select an answer', trigger: 'blur'},
                ],
                investment_preference: [
                    {required: true, message: 'Please select an answer', trigger: 'blur'},
                ],
                risk_tolerance: [
                    {required: true, message: 'Please select an answer', trigger: 'blur'},
                ]
            },
            loading: false
        }
    },
    methods: {
        handleRegister() {
            this.$refs.registerForm.validate(valid => {
                if (valid) {
                    this.loading = true;
                    this.$axios.post(this.$httpUrl + '/register', this.registerForm)
                        .then(res => {
                            if (res.data.code === 200) {
                                this.$message.success('Register successfully');
                                sessionStorage.setItem('user', res.data.data)
                                this.$router.replace('/index')
                            } else {
                                this.$message.error(res.data.msg);
                            }
                        })
                        .catch(error => {
                            this.$message.error('Register failed');
                            console.error(error);
                        })

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

