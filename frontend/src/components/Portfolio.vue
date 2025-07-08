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
            <!--            <el-switch-->
            <!--                v-model="rolling"-->
            <!--                active-text="Rolling Backtest"-->
            <!--                inactive-text="Buy & Hold"-->
            <!--                style="margin-left: 10px;"-->
            <!--            ></el-switch>-->

            <el-button
                type="primary"
                style="margin-left: 5px"
                @click="loadGet"
                icon="el-icon-search"
            >
                Show
            </el-button>
        </div>

        <div class="charts-container" v-loading="loadingChart" element-loading-text="Loading charts..."
             element-loading-background="rgba(255, 255, 255, 0.8)">
            <template v-if="showCharts">
                <div class="chart-row">
                    <div class="chart-half" ref="pieChart"></div>
                    <div class="chart-half" ref="heatmapChart"></div>
                </div>
                <div class="chart-large" ref="lineChart"></div>
                <div class="description">
                    <h3>Portfolio Summary</h3>
                    <p>{{ descriptionText }}</p>
                </div>
            </template>
            <template v-else>
                <div class="empty-message">
                    <p>Please select ETFs and click <strong>Show</strong> to visualize your portfolio.</p>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
import * as echarts from "echarts";

export default {
    name: "Portfolio",
    data() {
        return {
            code: [],
            loadingCodes: false,
            codes: [],
            showCharts: false,
            rolling: false,
            loadingChart: false,
            descriptionText:
                "This portfolio contains a diversified selection of ETFs with varying levels of risk and return, aiming to balance long-term growth with stability.",
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
            if (this.code.length === 0) {
                this.$message.warning("Please select at least one ETF.");
                return;
            }
            this.loadingChart = true;
            this.$axios
                .get(this.$httpUrl + "/compute", {
                    params: {
                        etf_list: this.code.join(","),
                        rolling: this.rolling,
                    },
                })
                .then((res) => res.data)
                .then((res) => {
                    if (res.code === 200) {
                        this.showCharts = true;
                        this.$nextTick(() => {
                            this.drawCharts(res.data);
                        });
                    } else {
                        this.$message.error("Failed to compute portfolio.");
                    }
                })
                .catch(() => {
                    this.$message.error("Error during computation.");
                })
                .finally(() => {
                    this.loadingChart = false;
                });
        },

        drawCharts(data) {
            if (data.weights && Object.keys(data.weights).length > 0) {
                const pieChart = echarts.init(this.$refs.pieChart);
                const pieData = Object.entries(data.weights).map(([name, value]) => ({
                    name,
                    value: (value * 100).toFixed(2),
                })).sort((a, b) => b.value - a.value);
                pieChart.setOption({
                    title: {text: "ETF Portfolio Allocation", left: "center"},
                    tooltip: {trigger: "item"},
                    legend: {
                        orient: 'vertical',
                        left: 'left',
                        data: pieData.map(item => item.name)
                    },
                    series: [{
                        name: "Allocation (%)",
                        type: "pie",
                        radius: "50%",
                        data: pieData,
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 20,
                                shadowOffsetX: 0,
                                shadowColor: "rgba(0, 0, 0, 0.5)",
                            },
                        },
                    }],
                });
            }
            if (data.correlation) {
                const heatmapChart = echarts.init(this.$refs.heatmapChart);
                const fontSize = Math.max(8, 16 - Math.floor(this.code.join(",").length / 4));
                const etfs = Object.keys(data.correlation);
                const correlationData = [];
                etfs.forEach((etf1, i) => {
                    etfs.forEach((etf2, j) => {
                        const val = data.correlation[etf1][etf2];
                        correlationData.push([i, j, val.toFixed(2)]);
                    });
                });
                heatmapChart.setOption({
                    title: {text: "ETF Correlation Matrix", left: "center"},
                    tooltip: {position: "top"},
                    xAxis: {type: "category", data: etfs},
                    yAxis: {type: "category", data: etfs},
                    visualMap: {
                        min: -1,
                        max: 1,
                        calculable: true,
                        orient: "horizontal",
                        left: "center",
                        bottom: "5%",
                    },
                    series: [{
                        name: "Correlation",
                        type: "heatmap",
                        data: correlationData,
                        label: {
                            show: true,
                            fontSize: fontSize,
                        },
                    }],
                });
            }

            const lineChart = echarts.init(this.$refs.lineChart);

            const series = [];
            let dates = null;

            for (const [name, curve] of Object.entries(data.cum_curve)) {
                const curveDates = Object.keys(curve);
                const curveValues = Object.values(curve).map(v => parseFloat(v.toFixed(2)));
                if (!dates) {
                    dates = curveDates;
                }
                series.push({
                    name,
                    type: "line",
                    smooth: true,
                    data: curveValues,
                });
            }

            lineChart.setOption({
                title: {text: "Cumulative Returns", left: "center"},
                tooltip: {trigger: "axis"},
                legend: {
                    type: 'scroll',
                    top: '5%'
                },

                xAxis: {type: "category", data: dates},
                yAxis: {type: "value"},
                series,
            });
            if (data.metrics) {
                var TotalReturn = data.metrics['Total Return']
                var Sharpe = data.metrics['Sharpe']
                var MaxDrawdown = data.metrics['Max Drawdown']
                var AnnualisedReturn = data.metrics['Annualised Return']
                var AnnualisedVol = data.metrics['Annualised Vol']
                this.descriptionText = `
                    Annual Return: ${(AnnualisedReturn * 100).toFixed(2)}%
                    Annual Volatility: ${(AnnualisedVol * 100).toFixed(2)}%
                    Sharpe Ratio: ${Sharpe.toFixed(2)}
                    Max Drawdown: ${(MaxDrawdown * 100).toFixed(2)}%
                    Total Return: ${(TotalReturn * 100).toFixed(2)}%`;
            } else {
                this.descriptionText = "No portfolio statistics available for rolling backtest.";
            }
        },
    },
    mounted() {
        this.fetchETFList();
    },
};
</script>

<style scoped>
.charts-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-top: 20px;
}

.chart-large {
    width: 100%;
    height: 450px;
    border: 1px solid #eee;
    border-radius: 10px;
    background: #fafafa;
    padding: 10px;
}

.chart-row {
    display: flex;
    gap: 10px;
}

.chart-half {
    flex: 1;
    height: 350px;
    border: 1px solid #eee;
    border-radius: 10px;
    background: #fafafa;
    padding: 10px;
}

.description {
    padding: 20px;
    border: 1px solid #eee;
    border-radius: 10px;
    background: #fff;
    line-height: 1.6;
}

.empty-message {
    grid-column: span 2;
    text-align: center;
    color: #999;
    font-size: 16px;
    padding: 40px 10px;
    border: 2px dashed #ccc;
    border-radius: 10px;
    background: #f9f9f9;
}

</style>
