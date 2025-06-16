<template>
    <div style="margin-inside: 5px">
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
                    <i class="el-icon-tickets"></i>
                    解析字段
                </template>
                <el-tag v-for="(item,index) in fields" :key="index" type="danger">{{ item.fieldName }}</el-tag>
            </el-descriptions-item>
        </el-descriptions>
        <div style="margin-top: 5px; border-radius: 4px; border: 1px solid #DCDFE6">
            <el-row>
                <el-col :span="16">
                    <div class="grid-content" id="code"
                         style=" border-radius: 4px; border-right: 1px solid #DCDFE6; border-bottom: 1px solid #DCDFE6; margin-right: 5px; margin-bottom: 2px;margin-left: 2px"
                         v-for="(item,index) in fields"
                         :key="index">
                        <div>
                            <el-row>
                                <el-col :span="7">
                                    <el-col :span="8">
                                        <div style="margin-left: 5px;margin-bottom: 5px;width: 60px">
                                            <p style="font-size:18px;font-weight: 900;">{{ item.fieldName }}</p>
                                        </div>
                                    </el-col>
                                    <el-col :span="4" :offset="12">
                                        <div style="width: 50px;height: 50px; margin-top: 5px">
                                            <el-image
                                                v-if="item.fieldName === 'images'"
                                                :src="fieldData[6].value"
                                                :preview-src-list="fieldData[5].value">
                                                <div slot="error" class="image-slot">
                                                </div>
                                            </el-image>
                                        </div>
                                    </el-col>
                                </el-col>
                                <el-col :span="12" :offset="1">
                                    <div style="margin-top: 5px">
                                        <el-input
                                            ref="text"
                                            :readonly=true
                                            type="textarea"
                                            :rows="2"
                                            placeholder="校验结果"
                                            v-model="item.fieldValue">
                                        </el-input>
                                    </div>
                                </el-col>
                                <el-col :span="1" :offset="1">
                                    <div style="margin-top: 15px">
                                        <el-button size="mini" type="warning" @click="check(index)">函数校验</el-button>
                                    </div>
                                </el-col>
                            </el-row>
                        </div>
                        <el-row>
                            <div style="border-top: 1px solid #DCDFE6">
                                <codemirror
                                    ref="code"
                                    :value="item.fieldCode"
                                    :options="cmOptions"
                                    class="code">
                                </codemirror>
                            </div>
                        </el-row>
                    </div>
                </el-col>
                <el-col :span="8">
                    <div class="grid-content" style="border-radius: 2px; margin-right: 5px">
                        <el-row>
                            <el-col :span="7">
                                <div style="margin-top: 15px">
                                    <el-button size="mini" type="success" @click="save">
                                        函数提交保存
                                    </el-button>
                                </div>
                            </el-col>
                            <el-col :span="5" :offset="6">
                                <div style="margin-top: 15px">
                                    <el-button size="mini" type="danger" @click="search">
                                        指定源码
                                    </el-button>
                                </div>
                            </el-col>
                            <el-col :span="5" :offset="1">
                                <div style="margin-top: 15px">
                                    <el-button size="mini" type="danger" @click="random">
                                        随机源码
                                    </el-button>
                                </div>
                            </el-col>
                        </el-row>
                        <el-row>
                            <el-input v-model="randomUrl" placeholder="网站url"
                                      style="margin-top: 10px;margin-bottom: 5px"></el-input>
                        </el-row>
                        <el-row>
                            <p style="font-size: 10px">源码大小:{{ size }}</p>
                        </el-row>
                        <!--                        <el-row :gutter="10">-->
                        <!--                            <el-col :span="8">-->
                        <!--                                <el-button type="primary" style="width: 100%;text-align: center" plain @click="openUrl">-->
                        <!--                                    url跳转-->
                        <!--                                </el-button>-->
                        <!--                            </el-col>-->
                        <!--                            <el-col :span="8">-->
                        <!--                                <el-button type="primary" style="width: 100%;text-align: center" plain>画面</el-button>-->
                        <!--                            </el-col>-->
                        <!--                            <el-col :span="8">-->
                        <!--                                <el-button type="primary" style="width: 100%;text-align: center" plain>源码跳转{{ size }}-->
                        <!--                                </el-button>-->
                        <!--                            </el-col>-->
                        <!--                        </el-row>-->
                        <el-row>
                            <div style="border-top: 1px solid #DCDFE6; margin-top: 5px" id="html">
                                <el-col>
                                    <el-table :data="fieldData" border stripe>
                                        <el-table-column label="名称" align="center" width="150%">
                                            <template slot-scope="scope">
                                                {{ scope.row.item }}
                                            </template>
                                        </el-table-column>
                                        <el-table-column label="值" align="center">
                                            <template slot-scope="scope">
                                                <div v-if="scope.row.item === 'url'">
                                                    <el-link :href="scope.row.value" target="_blank" :underline=false
                                                             style="font-size: 12px">{{ scope.row.value }}
                                                    </el-link>
                                                </div>
                                                <div v-else-if="scope.row.item === 'image'">
                                                    <el-link :href="scope.row.value" target="_blank" :underline=false
                                                             style="font-size: 12px">{{ scope.row.value }}
                                                    </el-link>
                                                </div>
                                                <div v-else-if="scope.row.item === 'images'">
                                                    <el-link :href="image" v-for="(image,index) in scope.row.value"
                                                             :key="index" target="_blank" :underline=false
                                                             style="font-size: 12px">{{ image }}
                                                    </el-link>
                                                </div>
                                                <div v-else>
                                                    {{ scope.row.value }}
                                                </div>
                                            </template>
                                        </el-table-column>
                                    </el-table>
                                </el-col>
                            </div>
                        </el-row>
                    </div>
                </el-col>
            </el-row>
        </div>

    </div>
</template>

<script>
import {codemirror} from 'vue-codemirror'
import 'codemirror/keymap/sublime'
import 'codemirror/addon/selection/active-line'
import 'codemirror/theme/idea.css'
import 'codemirror/addon/display/autorefresh'

require('codemirror/addon/fold/indent-fold.js')
import 'codemirror/addon/lint/lint'
import 'codemirror/addon/lint/lint.css'
import 'codemirror/addon/lint/json-lint'
import "codemirror/addon/search/match-highlighter.js"
import "codemirror/addon/hint/show-hint.css"
import "codemirror/addon/hint/show-hint.js"
import "codemirror/addon/hint/anyword-hint.js"
import "codemirror/mode/htmlmixed/htmlmixed.js"

require("codemirror/mode/python/python");
export default {
    name: "ParseItem",
    data() {
        return {
            name: this.$route.params.name,
            count: 0,
            state: '',
            fields: [],
            size: '',
            randomUrl: '',
            fieldData: [
                {
                    item: "url",
                    value: '',
                },
                {
                    item: "name",
                    value: '',
                },
                {
                    item: "description",
                    value: '',
                },
                {
                    item: "price",
                    value: '',
                },
                {
                    item: "detail_cat",
                    value: ''
                },
                {
                    item: "images",
                    value: ''
                },
                {
                    item: "image",
                    value: ''
                },
            ],
            cmOptions: {
                mode: 'text/x-python',
                theme: 'idea',
                keyMap: "sublime",
                line: true,
                matchTags: {bothTags: true},
                lineNumbers: true,
                lineWrapping: false,
                tabSize: 4,
                autorefresh: true,
                viewportMargin: Infinity,
                indentUnit: 2,
                smartIndent: true,
                firstLineNumber: 1,
                autocorrect: true,
                spellcheck: true,
                styleActiveLine: true,
            },
        }
    },
    components: {codemirror},
    methods: {
        search() {
            this.$axios.get(this.$httpUrl + '/searchURL', {
                params: {
                    web: this.name,
                    url: this.randomUrl
                }
            }).then(res => res.data).then(res => {
                if (res.code === 200) {
                    let data = res.data[0]
                    this.randomUrl = data.url
                    let byteSize = data['html'].length * 2;
                    let kiloByteSize = byteSize / 1024;
                    this.size = Math.round(kiloByteSize) + 'kb'
                    this.fieldData[0].value = data.url
                    this.fieldData[1].value = data.name != null ? data.name : ''
                    this.fieldData[2].value = data.description != null ? data.description : ''
                    this.fieldData[3].value = data.price != null ? data.price : ''
                    this.fieldData[4].value = data.detail_cat != null ? data.detail_cat : ''
                    this.fieldData[5].value = data.images != null ? data.images : ''
                    this.fieldData[6].value = data.image != null ? data.image : ''
                    this.$message({
                        message: '获取源码成功',
                        type: 'success'
                    });
                } else {
                    console.log('获取源码失败')
                }
            })
        },
        random() {
            this.$axios.get(this.$httpUrl + '/randomFields', {
                params: {
                    web: this.name,
                    number: 1
                }
            }).then(res => res.data).then(res => {
                if (res.code === 200) {
                    let data = res.data[0]
                    this.randomUrl = data.url
                    let byteSize = data['html'].length * 2;
                    let kiloByteSize = byteSize / 1024;
                    this.size = Math.round(kiloByteSize) + 'kb'
                    this.fieldData[0].value = data.url
                    this.fieldData[1].value = data.name != null ? data.name : ''
                    this.fieldData[2].value = data.description != null ? data.description : ''
                    this.fieldData[3].value = data.price != null ? data.price : ''
                    this.fieldData[4].value = data.detail_cat != null ? data.detail_cat : ''
                    this.fieldData[5].value = data.images != null ? data.images : ''
                    this.fieldData[6].value = data.image != null ? data.image : ''
                    this.$message({
                        message: '获取源码成功',
                        type: 'success'
                    });
                } else {
                    console.log('获取源码失败')
                }
            })
        },
        save() {
            for (let i = 0; i < this.fields.length; i++) {
                this.check(i)
            }
            this.$message({
                message: '保存成功',
                type: 'success'
            });
            this.loadFields()
        },
        loadFields() {
            this.$axios.get(this.$httpUrl + '/searchURL', {
                params: {
                    web: this.name,
                    url: this.randomUrl
                }
            }).then(res => res.data).then(res => {
                if (res.code === 200) {
                    let data = res.data[0]
                    this.randomUrl = data.url
                    let byteSize = data['html'].length * 2;
                    let kiloByteSize = byteSize / 1024;
                    this.size = Math.round(kiloByteSize) + 'kb'
                    this.fieldData[0].value = data.url
                    this.fieldData[1].value = data.name != null ? data.name : ''
                    this.fieldData[2].value = data.description != null ? data.description : ''
                    this.fieldData[3].value = data.price != null ? data.price : ''
                    this.fieldData[4].value = data.detail_cat != null ? data.detail_cat : ''
                    this.fieldData[5].value = data.images != null ? data.images : ''
                    this.fieldData[6].value = data.image != null ? data.image : ''
                }
            })
        },
        check(index) {
            let funcString = this.$refs.code[index].codemirror.getValue()
            let funcName = this.fields[index].fieldName
            this.$axios.post(this.$httpUrl + '/parseField', {
                website: this.name,
                url: this.randomUrl,
                func_string: funcString,
                func_name: funcName
            }).then(res => res.data).then(res => {
                if (res.code === 200) {
                    console.log(res.data)
                    this.$refs.text[index].value = res.data
                    this.$message({
                        message: '校验成功',
                        type: 'success'
                    });
                } else {
                    this.$refs.text[index].value = res.data
                    this.$message({
                        message: '校验失败',
                        type: 'error'
                    });
                }
            })
            this.loadFields()
        },
        back() {
            this.$router.go(-1)
        },
        loadGet() {
            this.$axios.get(this.$httpUrl + '/parse', {
                params: {
                    name: this.name,
                }
            }).then(res => res.data).then(res => {
                if (res.code === 200) {
                    console.log(res.data)
                    this.state = res.data[0].state
                    this.count = res.data[0].count
                    let dataKeys = Object.keys(res.data[0].parse_rules)
                    let dataValues = Object.values(res.data[0].parse_rules)
                    console.log(dataKeys.length)
                    for (let i = 0; i < dataKeys.length; i++) {
                        const obj = {'fieldName': null, 'fieldValue': '', 'fieldCode': ''};
                        obj['fieldName'] = dataKeys[i];
                        obj['fieldCode'] = dataValues[i].trim();
                        this.fields.push(obj);
                    }
                    console.log(this.fields)
                } else {
                    console.log('获取信息失败')
                }
            })
        },
    },
    beforeMount() {
        this.loadGet()
        this.$nextTick(() => {
            for (let i = 0; i < this.fields.length; i++) {
                let field = 'code_' + this.fields[i]['fieldName']
                const codeMirror = this.$refs[field]
                const value = codeMirror.editor.getValue()
                console.log(value)
            }
        })
    },
}
</script>

<style lang="scss">

</style>
