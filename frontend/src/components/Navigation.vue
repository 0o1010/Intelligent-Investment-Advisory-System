<template>
    <el-menu style="height: 100%;margin: 0;padding: 0;" background-color="#3D4145" text-color="#fff" router
             active-text-color="#409eff" default-active="/main" :collapse="isCollapse" :collapse-transition="false">

        <el-menu-item index="/main">
            <i class="el-icon-monitor"></i>
            <template slot="title">Visualization</template>
        </el-menu-item>
        <el-menu-item index="/llm">
            <i class="el-icon-cpu"></i>
            <span slot="title">LLM</span>
        </el-menu-item>
        <el-menu-item index="/suggestion">
            <i class="el-icon-document"></i>
            <span slot="title">Suggestion</span>
        </el-menu-item>
        <el-menu-item index="/modify">
            <i class="el-icon-edit"></i>
            <span slot="title">Modify Info</span>
        </el-menu-item>
    </el-menu>

</template>

<script>
export default {
    name: "Navigation",
    data() {
        return {
            // isCollapse: true
        }
    },
    props: {
        isCollapse: Boolean
    },
    created() {
        this.$router.push('/main')
    }
}

</script>

<style lang="scss" scoped>
.el-header {
    background-color: #B3C0D1;
    color: #333;
    line-height: 60px;
}

.el-aside {
    color: #333;
}

</style>
