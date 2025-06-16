<template>
    <div>
        <div style="margin-bottom: 5px">
            <el-select v-model="model" filterable placeholder="Select a NN model" style="margin-left: 5px">
                <el-option
                    v-for="item in models"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                </el-option>
            </el-select>
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

            <el-card :body-style="{ padding: '20px' }" v-loading="loading" style="margin-top: 10px">
                <e-charts
                    class="chart"
                    :option="chartOption"
                    :autoresize="true"
                    style="height: 600px;"
                />
            </el-card>


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
            model: '',
            loading:false,
            models: [
                {
                    value: '',
                    label: ''
                }, {
                    value: 'GRU',
                    label: 'GRU'
                }, {
                    value: 'LSTM',
                    label: 'LSTM'
                }, {
                    value: 'RNN',
                    label: 'RNN'
                }
            ],
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
                shortcuts: [
                    {
                        text: 'Half year',
                        onClick(picker) {
                            const end = new Date();
                            const start = new Date();
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 180);
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
                    }, {
                        text: 'Three years',
                        onClick(picker) {
                            const end = new Date();
                            const start = new Date();
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 365 * 3);
                            picker.$emit('pick', [start, end]);
                        }
                    }
                ]
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
            this.model = ''
            this.searchDate = ''
            this.chartOption = this.emptyChartOption
        },
        loadGet() {
    if (!this.code || !this.searchDate || this.searchDate.length < 2) {
        this.chartOption = this.emptyChartOption;
        return;
    }

    this.loading = true;

    this.$axios.get(this.$httpUrl + '/getPrice', {
        params: {
            model: this.model,
            code: this.code,
            start_date: this.searchDate[0],
            end_date: this.searchDate[1],
        }
    }).then(res => res.data).then(res => {
        if (res.code === 200) {
            const train = res.data.train;
            const valid = res.data.valid;

            const closePrice = train.map(item => item.close);
            const predictedPrice = valid.map(item => item.Prediction);
            const dateLabels = valid.map(item => item.date);

            this.chartOption = {
                title: {
                    text: this.code + " history and prediction chart",
                    left: "center",
                    top: 10,
                    textStyle: {
                        fontSize: 18
                    }
                },
                tooltip: {
                    trigger: "axis",
                    axisPointer: {type: "cross"},
                },
                legend: {
                    data: ["Actual Close", "Predicted"],
                    top: 50,
                    left: "center"
                },
                grid: {
                    left: "10%",
                    right: "10%",
                    bottom: "15%",
                    top: 90
                },
                xAxis: {
                    type: "category",
                    data: dateLabels,
                    scale: true,
                    boundaryGap: false,
                    axisLine: {onZero: false},
                },
                yAxis: {
                    scale: true,
                    splitArea: {show: true},
                },
                series: [
                    {
                        name: "Actual Close",
                        type: "line",
                        data: closePrice,
                        smooth: true,
                        showSymbol: false,
                        lineStyle: {width: 2},
                    },
                    {
                        name: "Predicted",
                        type: "line",
                        data: predictedPrice,
                        smooth: true,
                        showSymbol: false,
                        lineStyle: {width: 2},
                    }
                ],
            };
        } else {
            this.chartOption = this.emptyChartOption;
            console.log('Fetch historical prices failed')
        }
    }).finally(() => {
        this.loading = false;
    });
}

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
