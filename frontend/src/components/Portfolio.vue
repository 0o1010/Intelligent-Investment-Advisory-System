<template>
    <div>
        <div style="margin-bottom: 5px">
            <el-select
                v-model="code"
                filterable
                multiple
                clearable
                collapse-tags
                :multiple-limit="20"
                placeholder="Choose up to 20 ETFs"
                style="margin-left: 5px"
                class="model-select"
                :loading="loadingCodes"
                :loading-text="'Loading...'"
                :no-match-text="'No matching ETF'"
            >
                <el-option
                    v-for="item in codes"
                    :key="item.value"
                    :label="item.value"
                    :value="item.value"
                >
                    <span style="font-weight: bold;">{{ item.value }}</span>
                    <span style="color: #999; float: right;">{{ item.label }}</span>
                </el-option>
            </el-select>
            <el-button type="primary" style="margin-left: 5px" @click="loadGet" icon="el-icon-search">Show</el-button>
        </div>
    </div>
</template>

<script>
export default {
    name: "Portfolio",
    data() {
        return {
            code: [],
            loadingCodes: false,
            codes: [],
        };
    },
    methods: {
        fetchETFList() {
            this.loadingCodes = true;
            this.$axios
                .get(this.$httpUrl + "/getAllETF")
                .then((res) => res.data)
                .then((res) => {
                    if (res.code === 200) {
                        this.codes = res.data;
                    } else {
                        this.$message.error("Failed to load ETF list.");
                    }
                })
                .catch(() => {
                    this.$message.error("Error while fetching ETF list.");
                })
                .finally(() => {
                    this.loadingCodes = false;
                });
        },
        loadGet() {

        }
    },
    mounted() {
        this.fetchETFList();
    },
};
</script>

<style scoped>
.model-select {
    width: 260px;
    margin-right: 10px;
}
</style>
