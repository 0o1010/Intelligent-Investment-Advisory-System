<template>
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div style="margin-top: 8px; cursor: pointer;">
            <i :class="icon" style="font-size: 20px" @click="collapse"></i>
        </div>

        <div style="flex: 1; text-align: center; line-height: 1.2;">
            <div style="font-size: 30px; font-weight: bold;">
                Intelligent Investment Advisory System
            </div>
            <div style="font-size: 11px; color: #888; max-width: 600px; margin: 0 auto; white-space: normal;">
                Disclaimer: All data and information on this website are for reference only and do not constitute any
                investment advice. Investing involves risks, and decisions should be made with caution.
            </div>
        </div>

        <el-dropdown>
            <span>user: {{ username }}</span>
            <i class="el-icon-arrow-down" style="margin-left: 5px"></i>
            <el-dropdown-menu slot="dropdown">
                <el-dropdown-item @click.native="logout">Logout</el-dropdown-item>
            </el-dropdown-menu>
        </el-dropdown>
    </div>
</template>


<script>
export default {
    name: "Header",
    props: {
        icon: String
    },
    data() {
        return {
            username: ""
        }
    },

    methods: {
        getUsername() {
            this.username = sessionStorage.getItem('user')
            console.log(this.username)
        },
        logout() {
            this.$confirm('Ensure to logout？', 'Warning', {
                confirmButtonText: 'Yes',
                cancelButtonText: 'No',
                type: 'warning',
                center: true
            }).then(() => {
                this.$message({
                    message: 'Logout successfully',
                    type: 'success'
                })
                this.$router.push('/')
                sessionStorage.clear()
            }).catch(() => {
                this.$message({
                    message: 'Cancel logout',
                    type: 'info'
                })
            })
        },
        collapse() {
            this.$emit('doCollapse')
        }
    },
    beforeMount() {
        this.getUsername()
    }
}
</script>

<style scoped>

</style>
