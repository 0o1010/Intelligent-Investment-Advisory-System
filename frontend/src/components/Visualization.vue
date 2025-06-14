<template>
    <div>
        <div style="margin-bottom: 5px">
            <el-select v-model="code" filterable placeholder="Choose an ETF" style="margin-left: 5px">
                <el-option
                    v-for="item in codes"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                </el-option>
            </el-select>
            <el-date-picker
                style="margin-left: 5px"
                v-model="searchDate"
                type="daterange"
                :picker-options="pickerOptions"
                format="yyyy-MM-dd"
                value-format="yyyy-MM-dd"
                range-separator="to"
                start-placeholder="start date"
                end-placeholder="end date"
                align="right">
            </el-date-picker>
            <el-button type="primary" style="margin-left: 5px" @click="loadGet" icon="el-icon-search">Show</el-button>
            <el-button type="success" @click="reset" icon="el-icon-refresh">Reset</el-button>

            <e-charts
                class="chart"
                :option="chartOption"
                :autoresize="true"
                style="height: 600px;"/>

        </div>

    </div>
</template>

<script>
import EChart from "vue-echarts";
import "echarts/lib/chart/candlestick";
import "echarts/lib/component/tooltip";
import "echarts/lib/component/title";
import "echarts/lib/component/grid";

export default {
    name: "Visualization",

    components: {
        "e-charts": EChart,
    },
    data() {
        return {
            code: '',
            codes: [
                {
                    value: '',
                    label: ''
                }, {
                    value: 'QQQ',
                    label: 'QQQ'
                }, {
                    value: 'EEM',
                    label: 'EEM'
                }, {
                    value: 'SPY',
                    label: 'SPY'
                }, {
                    value: 'GLD',
                    label: 'GLD'
                },
            ],
            pickerOptions: {
                shortcuts: [{
                    text: 'One week',
                    onClick(picker) {
                        const end = new Date();
                        const start = new Date();
                        start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
                        picker.$emit('pick', [start, end]);
                    }
                }, {
                    text: 'One month',
                    onClick(picker) {
                        const end = new Date();
                        const start = new Date();
                        start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
                        picker.$emit('pick', [start, end]);
                    }
                }, {
                    text: 'One year',
                    onClick(picker) {
                        const end = new Date();
                        const start = new Date();
                        start.setTime(start.getTime() - 3600 * 1000 * 24 * 365);
                        picker.$emit('pick', [start, end]);
                    }
                }]
            },
            searchDate: '',
            emptyChartOption: {
                title: {
                    text: "ETF history price chart",
                    left: "center",
                },
                tooltip: {
                    trigger: "axis",
                    axisPointer: {
                        type: "cross",
                    },
                },
                xAxis: {
                    type: "category",
                    data: [],
                    scale: true,
                    boundaryGap: false,
                    axisLine: {onZero: false},
                },
                yAxis: {
                    scale: true,
                    splitArea: {show: true},
                },
                grid: {
                    left: "10%",
                    right: "10%",
                    bottom: "15%",
                },
                series: [
                    {
                        name: "Close price",
                        type: "line",
                        data: [],
                        smooth: true,
                        showSymbol: false,
                        lineStyle: {
                            width: 2,
                        },
                    },
                ],
            },
            chartOption: {},
        }
    },

    methods: {
        reset() {
            this.code = ''
            this.searchDate = ''
            this.chartOption = this.emptyChartOption
        },
        loadGet() {
            if (!this.code || !this.searchDate || this.searchDate.length < 2) {
                this.chartOption = this.emptyChartOption;
                return;
            }
            this.$axios.get(this.$httpUrl + '/getPrice', {
                params: {
                    code: this.code,
                    start_date: this.searchDate[0],
                    end_date: this.searchDate[1],
                }
            }).then(res => res.data).then(res => {
                if (res.code === 200) {
                    const rawData = res.data;
                    console.log(rawData);
                    const categoryData = [];
                    const values = [];

                    rawData.forEach((item) => {
                        categoryData.push(item.date);
                        values.push([item.open, item.close, item.low, item.high]);
                    });

                    this.chartOption = {
                        title: {
                            text: this.code + " history price chart",
                            left: "center",
                        },
                        tooltip: {
                            trigger: "axis",
                            axisPointer: {
                                type: "cross",
                            },
                        },
                        xAxis: {
                            type: "category",
                            data: categoryData,
                            scale: true,
                            boundaryGap: false,
                            axisLine: {onZero: false},
                        },
                        yAxis: {
                            scale: true,
                            splitArea: {
                                show: true,
                            },
                        },
                        grid: {
                            left: "10%",
                            right: "10%",
                            bottom: "15%",
                        },
                        series: [
                            {
                                name: "Close price",
                                type: "line",
                                data: rawData.map(item => item.close),
                                smooth: true,
                                showSymbol: false,
                                lineStyle: {
                                    width: 2,
                                },
                            },
                        ],

                    };
                } else {
                    this.chartOption = this.emptyChartOption;
                    console.log('Fetch historical prices failed')
                }
            })
        },
    },
    mounted() {
        this.loadGet();
    },
    beforeMount() {
        this.loadGet()
    }
}
</script>

<style scoped>

</style>
