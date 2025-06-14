<template>
    <div id="show" class="main_container" style="height:100%;overflow: auto;">
        <el-backtop target=".main_container"></el-backtop>
        <el-descriptions class="margin-top" title="编写解析函数" :column="3" border>
            <template slot="extra">
                <el-button type="primary" size="small" @click="back">返回</el-button>
            </template>
            <el-descriptions-item>
                <template slot="label">
                    <i class="el-icon-document"></i>
                    网站名称
                </template>
                {{ name }}
            </el-descriptions-item>
            <el-descriptions-item>
                <template slot="label">
                    <i class="el-icon-s-grid"></i>
                    详情页数量
                </template>
                {{ count }}
            </el-descriptions-item>
            <el-descriptions-item>
                <template slot="label">
                    <i class="el-icon-paperclip"></i>
                    网站状态
                </template>
                <el-tag style="margin-left: 5px"
                        :type="state === 5 ? 'success' : 'danger'"
                        disable-transitions>{{ state === 5 ? '已解析' : '未解析' }}
                </el-tag>
            </el-descriptions-item>
            <el-descriptions-item>
                <template slot="label">
                    <i class="el-icon-money"></i>
                    网站货币类型
                </template>
                {{ currency }}
            </el-descriptions-item>
            <el-descriptions-item>
                <template slot="label">
                    <i class="el-icon-shopping-cart-full"></i>
                    国家
                </template>
                {{ country }}
            </el-descriptions-item>
            <el-descriptions-item>
                <template slot="label">
                    <i class="el-icon-info"></i>
                    网站所属类别
                </template>
                {{ website_cat }}
            </el-descriptions-item>
        </el-descriptions>
        <div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center;">
            <div style="width:20vw; margin: 5px; border-radius: 4px; border: 1px solid #DCDFE6; float: left"
                 v-for="(item,index) in items" :key="index">
                <el-card :body-style="{ padding: '0px' }">
                    <div style="text-align: center;">
                        <el-image
                            lazy
                            style="width: 100px; height: 100px"
                            :src="item.image"
                            :preview-src-list="item.images">
                        </el-image>
                    </div>
                    <div style="padding: 14px;">
                        <el-link style="font-size: 14px" :href="item.url" :underline=false target="_blank">
                            链接：{{ item.url }}
                        </el-link>
                        <p style="font-size: 14px">名称：{{ item.name }}</p>
                        <p style="font-size: 14px">价格：{{ item.price }}</p>
                        <p style="font-size: 14px">类目：{{ item.detail_cat }}</p>
                        <p style="font-size: 14px">描述：{{ item.description }}</p>
                    </div>
                </el-card>
            </div>
        </div>
        <infinite-loading
            ref="infiniteLoading"
            distance=100
            @infinite="infiniteHandler"
        >
            <div slot="spinner">加载中...</div>
            <div slot="no-more">没有更多内容了</div>
            <div slot="no-results">
                暂无数据
            </div>
        </infinite-loading>
    </div>
</template>

<script>
import InfiniteLoading from "vue-infinite-loading";

export default {
    name: "ShowItem",
    components: {InfiniteLoading},
    data() {
        return {
            name: this.$route.params.name,
            count: 0,
            state: '',
            country: '',
            currency: '',
            website_cat: '',
            items: [],
            current_page: 1,
            page_size: 20,
        }
    },
    methods: {
        infiniteHandler($state) {
            setTimeout(() => {
                console.log(this.items.length / 20)
                this.$axios.get(this.$httpUrl + '/showData', {
                    params: {
                        name: this.name,
                        current_page: Math.ceil(this.items.length / 20) + 1,
                        page_size: this.page_size,
                    }
                }).then(res => res.data).then(res => {
                    if (res.code === 200) {
                        console.log(res.data)
                        this.items = this.items.concat(res.data)
                    } else {
                        console.log('获取信息失败')
                        $state.complete();
                    }
                })
                $state.loaded();
            }, 1000);
        },
        back() {
            this.$router.go(-1)
        },
        loadGet() {
            this.$axios.get(this.$httpUrl + '/show', {
                params: {
                    name: this.name,
                }
            }).then(res => res.data).then(res => {
                if (res.code === 200) {
                    console.log(res.data)
                    this.state = res.data[0].state
                    this.count = res.data[0].count
                    this.country = res.data[0].country
                    this.currency = res.data[0].currency
                    this.website_cat = res.data[0].website_cat
                } else {
                    console.log('获取信息失败')
                }
            })
            this.$axios.get(this.$httpUrl + '/showData', {
                params: {
                    name: this.name,
                    current_page: this.current_page,
                    page_size: this.page_size,
                }
            }).then(res => res.data).then(res => {
                if (res.code === 200) {
                    console.log(res.data)
                    this.items = res.data
                } else {
                    console.log('获取信息失败')
                }
            })
        },
    },
    beforeMount() {
        this.loadGet()
    }
}
</script>
<style scoped>

</style>
