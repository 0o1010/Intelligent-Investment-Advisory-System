<template>
    <div class="login-container">
        <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form" auto-complete="on"
                 label-position="left">
            <div class="title-container">
                <h3 class="title">User Login</h3>
            </div>

            <el-form-item prop="username">
                <span class="svg-container">
                    <i class="el-icon-user"/>
                </span>
                <el-input
                    ref="username"
                    v-model="loginForm.username"
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
                <el-input placeholder="Input password" v-model="loginForm.password" show-password
                          @keydown.enter.native="handleLogin"></el-input>
            </el-form-item>

            <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 30px;">
                <el-button :loading="loading" type="primary" style="width: 50%;"
                           @click.native.prevent="handleLogin">Login
                </el-button>
                <el-button :loading="loading" type="success" style="width: 50%;"
                           @click.native.prevent="handleRegister">Register
                </el-button>
            </div>
        </el-form>
    </div>

</template>

<script>


export default {
    name: "Login",
    data() {
        const validatePassword = (rule, value, callback) => {
            if (value.length === 0) {
                callback(new Error('Empty password!'))
            } else {
                callback()
            }
        }
        return {
            loginForm: {
                username: 'demo',
                password: '123456'
            },
            loginRules: {
                password: [{required: true, trigger: 'blur', validator: validatePassword}]
            },
            loading: false,
            redirect: undefined
        }
    },
    methods: {
        handleLogin() {
            this.$refs.loginForm.validate(valid => {
                if (valid) {
                    this.loading = true
                    this.$axios.post(this.$httpUrl + '/login', this.loginForm).then(res => res.data).then((res) => {
                        if (res.code === 200) {
                            console.log(res.data)
                            sessionStorage.setItem('user', res.data)
                            this.$router.replace('/index')
                        } else {
                            this.$message.error('Login failed');
                        }
                        this.loading = false
                    }).catch(() => {
                        this.$message.error('Login failed');
                        this.loading = false
                    })
                } else {
                    console.log('error submit!!')
                    return false
                }
            })
        },
        handleRegister() {
            this.$router.push('/register')
        }
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
    }
}
</style>

<style lang="scss" scoped>
$bg: #2d3a4b;
$dark_gray: #889aa4;
$light_gray: #eee;

.login-container {
    width: 100%;
    height: 100%;
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
}
</style>

