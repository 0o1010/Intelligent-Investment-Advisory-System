<template>
    <el-container style="height: 100%; border: 1px solid #eee">
        <el-aside :width="aside_width" style="background-color: rgb(238, 241, 246);height: 100%;margin-left: -1px">
            <Navigation :isCollapse="isCollapse"></Navigation>
        </el-aside>

        <el-container style="height: 100%">
            <el-header
                style="text-align: right; font-size: 12px;height: auto;border-bottom: rgba(168,168,168,0.3) 1px solid">
                <Header @doCollapse="doCollapse" :icon="icon"></Header>
            </el-header>

            <el-main style="height: 100%">
                <router-view></router-view>
            </el-main>
        </el-container>
    </el-container>
</template>

<script>
import Navigation from "@/components/Navigation";
import Header from "@/components/Header";

export default {
    name: "Index",
    components: {Header, Navigation},
    data() {
        return {
            isCollapse: false,
            aside_width: '200px',
            icon: 'el-icon-s-fold'
        }
    },
    methods: {
        doCollapse() {
            this.isCollapse = !this.isCollapse
            if (!this.isCollapse) {
                this.icon = 'el-icon-s-fold'
                this.aside_width = '200px'
            } else {
                this.icon = 'el-icon-s-unfold'
                this.aside_width = '64px'
            }
        }
    }
}
</script>

<style lang="scss" scoped>
.el-header {
    background-color: #ffffff;
    color: #333;
    line-height: 60px;
}

.el-aside {
    color: #333;
}
</style>
